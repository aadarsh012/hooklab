"""Evaluation harness for the HookLab pipeline."""

import logging
import random
from typing import Dict, List, Optional

import numpy as np

from agents.llm import call_llm
from agents.pipeline import analyze
from embeddings.store import HookVectorStore
from scoring.data import load_hooks
from scoring.persist import load_model

logger = logging.getLogger(__name__)

TEST_PATH = "data/processed/test.jsonl"

# Shared instances — loaded once, reused across all eval functions
_store = None
_model = None


def _get_store() -> HookVectorStore:
    global _store
    if _store is None:
        _store = HookVectorStore()
    return _store


def _get_model():
    global _model
    if _model is None:
        _model = load_model()
    return _model


# --- Task 1: Batch ML predictions ---


def evaluate_predictions(test_path: str = TEST_PATH) -> Dict:
    """Run predictions on all test hooks in batch, compare with true labels.

    Loads model and store once, encodes all hooks in a single batch,
    then runs predictions on the batch.

    Returns dict with:
        accuracy, precision, recall, f1, confusion_matrix,
        per_hook_results (list of dicts)
    """
    hooks = load_hooks(test_path)
    logger.info("Evaluating %d test hooks", len(hooks))

    store = _get_store()
    model = _get_model()

    # Batch encode all hooks at once
    texts = [h["hook_text"] for h in hooks]
    embeddings = store.model.encode(texts).tolist()
    X = np.array(embeddings)

    # Batch predict
    y_pred = model.predict(X)
    y_proba = model.predict_proba(X)

    results = []
    correct = 0
    tp = fp = tn = fn = 0

    label_names = ["weak", "strong"]

    for i, hook in enumerate(hooks):
        true_label = hook["label"]
        pred_label = label_names[y_pred[i]]
        confidence = float(y_proba[i][y_pred[i]])
        is_correct = pred_label == true_label

        if is_correct:
            correct += 1

        # Confusion matrix counts (positive = strong)
        if true_label == "strong" and pred_label == "strong":
            tp += 1
        elif true_label == "weak" and pred_label == "strong":
            fp += 1
        elif true_label == "weak" and pred_label == "weak":
            tn += 1
        elif true_label == "strong" and pred_label == "weak":
            fn += 1

        results.append({
            "hook_id": hook.get("hook_id", ""),
            "hook_text": hook["hook_text"],
            "true_label": true_label,
            "predicted_label": pred_label,
            "confidence": confidence,
            "correct": is_correct,
        })

    total = len(hooks)
    accuracy = correct / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    logger.info("Accuracy: %.2f%% (%d/%d)", accuracy * 100, correct, total)

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "confusion_matrix": [[tn, fp], [fn, tp]],
        "total": total,
        "correct": correct,
        "per_hook_results": results,
    }


# --- Task 2: Predicted vs Actual ---


def predicted_vs_actual(prediction_results: Dict) -> Dict:
    """Analyze predictions grouped by true label.

    Returns dict with per-label stats, overconfident wrongs, underconfident rights.
    """
    results = prediction_results["per_hook_results"]

    # Group by true label
    strong_hooks = [r for r in results if r["true_label"] == "strong"]
    weak_hooks = [r for r in results if r["true_label"] == "weak"]

    def _group_stats(hooks: List[Dict]) -> Dict:
        if not hooks:
            return {"count": 0, "accuracy": 0, "mean_confidence": 0}
        correct = sum(1 for h in hooks if h["correct"])
        return {
            "count": len(hooks),
            "accuracy": correct / len(hooks),
            "mean_confidence": sum(h["confidence"] for h in hooks) / len(hooks),
        }

    # Overconfident wrong: high confidence but wrong
    overconfident = [
        r for r in results
        if not r["correct"] and r["confidence"] > 0.8
    ]

    # Underconfident correct: low confidence but right
    underconfident = [
        r for r in results
        if r["correct"] and r["confidence"] < 0.6
    ]

    return {
        "strong_stats": _group_stats(strong_hooks),
        "weak_stats": _group_stats(weak_hooks),
        "overconfident_wrong": overconfident,
        "underconfident_correct": underconfident,
    }


# --- Task 3: Rewriter evaluation with LLM-as-judge ---


def evaluate_rewrites(test_path: str = TEST_PATH, n: int = 20) -> Dict:
    """Evaluate rewrites using LLM-as-judge (blind comparison).

    Selects up to n weak hooks, generates rewrites via analyze(),
    then asks an LLM judge which hook is stronger (without revealing which is original).

    Returns dict with preference_rate, per_hook_judgments.
    """
    hooks = load_hooks(test_path)
    weak_hooks = [h for h in hooks if h["label"] == "weak"][:n]

    if not weak_hooks:
        logger.warning("No weak hooks found for rewriter evaluation")
        return {"preference_rate": 0, "upgrade_rate": 0, "judgments": []}

    logger.info("Evaluating rewrites for %d weak hooks", len(weak_hooks))

    judgments = []

    for i, hook in enumerate(weak_hooks):
        logger.info("  [%d/%d] Analyzing: %s", i + 1, len(weak_hooks), hook["hook_text"][:50])

        try:
            analysis = analyze(hook["hook_text"])
        except Exception as e:
            logger.warning("  Failed to analyze hook: %s", e)
            continue

        if not analysis.rewrites:
            logger.warning("  No rewrites generated")
            continue

        # Judge each rewrite against the original
        for rewrite in analysis.rewrites:
            judgment = _judge_pair(hook["hook_text"], rewrite.rewritten_hook)
            judgments.append({
                "original": hook["hook_text"],
                "rewrite": rewrite.rewritten_hook,
                "target_dimension": rewrite.target_dimension,
                "changes_made": rewrite.changes_made,
                "judge_prefers": judgment["preferred"],
                "judge_reason": judgment["reason"],
            })

    # Compute preference rate
    total_judgments = len(judgments)
    rewrite_wins = sum(1 for j in judgments if j["judge_prefers"] == "rewrite")
    preference_rate = rewrite_wins / total_judgments if total_judgments > 0 else 0

    logger.info("Rewrite preference rate: %.0f%% (%d/%d)",
                preference_rate * 100, rewrite_wins, total_judgments)

    return {
        "preference_rate": preference_rate,
        "total_judgments": total_judgments,
        "rewrite_wins": rewrite_wins,
        "judgments": judgments,
    }


def _judge_pair(original: str, rewrite: str) -> Dict:
    """Ask LLM to blindly judge which hook is stronger.

    Randomly assigns A/B to avoid position bias.
    """
    # Randomize order to avoid position bias
    if random.random() > 0.5:
        hook_a, hook_b = original, rewrite
        a_is_original = True
    else:
        hook_a, hook_b = rewrite, original
        a_is_original = False

    system = (
        "You are a blind judge evaluating short-form video hooks. "
        "You do not know which hook is the original and which is a rewrite. "
        "Judge purely on hook quality: curiosity gap, specificity, and stopping power."
    )

    prompt = (
        f'Hook A: "{hook_a}"\n'
        f'Hook B: "{hook_b}"\n\n'
        "Which is a stronger opener for a short-form fitness video? "
        "Answer with ONLY the letter (A or B) on the first line, "
        "then one sentence explaining why."
    )

    response = call_llm(system, prompt)
    lines = response.strip().split("\n", 1)
    choice = lines[0].strip().upper()
    reason = lines[1].strip() if len(lines) > 1 else ""

    # Map back to original/rewrite
    if choice == "A":
        preferred = "original" if a_is_original else "rewrite"
    elif choice == "B":
        preferred = "rewrite" if a_is_original else "original"
    else:
        preferred = "unclear"
        reason = f"Judge gave unclear answer: {response[:100]}"

    return {"preferred": preferred, "reason": reason}


# --- Task 4: Score rewrites with classifier ---


def score_rewrites(rewrite_results: Dict) -> Dict:
    """Score both original and rewritten hooks with the classifier.

    Computes 'upgrade rate' — % of rewrites classified as strong
    when the original was classified as weak.
    """
    judgments = rewrite_results.get("judgments", [])
    if not judgments:
        return {"upgrade_rate": 0, "scored": []}

    store = _get_store()
    model = _get_model()
    label_names = ["weak", "strong"]

    # Batch encode all originals + rewrites at once
    all_texts = []
    for j in judgments:
        all_texts.append(j["original"])
        all_texts.append(j["rewrite"])

    all_embeddings = store.model.encode(all_texts).tolist()
    X_all = np.array(all_embeddings)
    y_all = model.predict(X_all)
    proba_all = model.predict_proba(X_all)

    scored = []
    upgrades = 0

    for i, j in enumerate(judgments):
        orig_idx = i * 2
        rw_idx = i * 2 + 1

        orig_label = label_names[y_all[orig_idx]]
        orig_conf = float(proba_all[orig_idx][y_all[orig_idx]])
        rw_label = label_names[y_all[rw_idx]]
        rw_conf = float(proba_all[rw_idx][y_all[rw_idx]])

        is_upgrade = orig_label == "weak" and rw_label == "strong"
        if is_upgrade:
            upgrades += 1

        scored.append({
            "original": j["original"],
            "original_label": orig_label,
            "original_confidence": orig_conf,
            "rewrite": j["rewrite"],
            "rewrite_label": rw_label,
            "rewrite_confidence": rw_conf,
            "is_upgrade": is_upgrade,
            "judge_prefers": j["judge_prefers"],
        })

    total = len(scored)
    upgrade_rate = upgrades / total if total > 0 else 0

    logger.info("Upgrade rate: %.0f%% (%d/%d)", upgrade_rate * 100, upgrades, total)

    return {
        "upgrade_rate": upgrade_rate,
        "upgrades": upgrades,
        "total": total,
        "scored": scored,
    }
