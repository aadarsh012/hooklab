"""
Train and evaluate the hook scoring model.

Usage: python scripts/train_scorer.py
"""

import logging
import sys
from datetime import datetime, timezone

sys.path.insert(0, ".")

from scoring.classifier import (
    evaluate_model,
    hook_length_baseline,
    majority_class_baseline,
    train_gradient_boosting,
    train_logistic,
)
from scoring.data import load_dataset
from scoring.persist import save_model
from scoring.report import generate_report
from scoring.schemas import EvalReport, FailureCase

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def main():
    # 1. Load data
    logger.info("Loading dataset...")
    data = load_dataset()

    X_train, y_train = data["X_train"], data["y_train"]
    X_test, y_test = data["X_test"], data["y_test"]
    train_hooks, test_hooks = data["train_hooks"], data["test_hooks"]
    test_ids = data["test_ids"]

    logger.info("Dataset: %d train (%d strong, %d weak), %d test (%d strong, %d weak)",
                len(y_train), int(y_train.sum()), int(len(y_train) - y_train.sum()),
                len(y_test), int(y_test.sum()), int(len(y_test) - y_test.sum()))

    # 2. Run baselines
    logger.info("Running baselines...")
    baseline_majority = majority_class_baseline(y_train, y_test)
    baseline_length = hook_length_baseline(train_hooks, test_hooks, y_train, y_test)

    baselines = [baseline_majority, baseline_length]
    for b in baselines:
        logger.info("  %s: accuracy=%.2f%%, precision=%.2f%%, recall=%.2f%%",
                     b.name, b.accuracy * 100, b.precision * 100, b.recall * 100)

    # 3. Train and evaluate models
    logger.info("Training logistic regression...")
    lr_model = train_logistic(X_train, y_train)
    lr_metrics = evaluate_model(lr_model, X_test, y_test, test_hooks, test_ids, "Logistic Regression")
    logger.info("  Logistic Regression: accuracy=%.2f%%, precision=%.2f%%, recall=%.2f%%",
                lr_metrics.accuracy * 100, lr_metrics.precision * 100, lr_metrics.recall * 100)

    logger.info("Training gradient boosting...")
    gb_model = train_gradient_boosting(X_train, y_train)
    gb_metrics = evaluate_model(gb_model, X_test, y_test, test_hooks, test_ids, "Gradient Boosting")
    logger.info("  Gradient Boosting: accuracy=%.2f%%, precision=%.2f%%, recall=%.2f%%",
                gb_metrics.accuracy * 100, gb_metrics.precision * 100, gb_metrics.recall * 100)

    models_metrics = [lr_metrics, gb_metrics]

    # 4. Pick best model
    best_metrics = max(models_metrics, key=lambda m: m.accuracy)
    best_model = lr_model if best_metrics.model_name == "Logistic Regression" else gb_model

    # If tied, prefer logistic regression (simpler)
    if lr_metrics.accuracy == gb_metrics.accuracy:
        best_model = lr_model
        best_metrics = lr_metrics

    logger.info("Best model: %s (accuracy=%.2f%%)", best_metrics.model_name, best_metrics.accuracy * 100)

    # 5. Save best model
    save_model(best_model)
    logger.info("Saved best model to scoring/trained_model.joblib")

    # 6. Failure analysis
    failures = []
    for pred in best_metrics.test_predictions:
        if pred.true_label != pred.predicted_label:
            notes = ""
            if pred.confidence > 0.8:
                notes = "High confidence wrong prediction"
            elif pred.confidence > 0.6:
                notes = "Moderate confidence wrong prediction"
            else:
                notes = "Borderline confidence"

            failures.append(FailureCase(
                hook_id=pred.hook_id,
                hook_text=pred.hook_text,
                true_label=pred.true_label,
                predicted_label=pred.predicted_label,
                confidence=pred.confidence,
                notes=notes,
            ))

    if failures:
        logger.info("Failure analysis: %d misclassified hooks", len(failures))
        for f in failures:
            logger.info("  [%s->%s] (conf=%.2f) %s", f.true_label, f.predicted_label,
                        f.confidence, f.hook_text[:80])
    else:
        logger.info("No misclassifications on test set")

    # 7. Generate report
    n_strong_train = int(y_train.sum())
    n_weak_train = int(len(y_train) - y_train.sum())
    n_strong_test = int(y_test.sum())
    n_weak_test = int(len(y_test) - y_test.sum())

    dataset_summary = (
        f"- Training: {len(y_train)} hooks ({n_strong_train} strong, {n_weak_train} weak)\n"
        f"- Test: {len(y_test)} hooks ({n_strong_test} strong, {n_weak_test} weak)\n"
        f"- Features: 384-dim sentence-transformer embeddings (all-MiniLM-L6-v2)"
    )

    report = EvalReport(
        baselines=baselines,
        models=models_metrics,
        failure_analysis=failures,
        generated_at=datetime.now(timezone.utc).isoformat(),
        dataset_summary=dataset_summary,
    )

    generate_report(report)
    logger.info("Evaluation report saved to eval/REPORT.md")

    # 8. Summary
    best_baseline_acc = max(b.accuracy for b in baselines)
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for b in baselines:
        print(f"  Baseline ({b.name}): {b.accuracy:.2%}")
    for m in models_metrics:
        diff = m.accuracy - best_baseline_acc
        sign = "+" if diff >= 0 else ""
        print(f"  {m.model_name}: {m.accuracy:.2%} ({sign}{diff:.2%} vs best baseline)")
    print(f"\n  Best model: {best_metrics.model_name}")
    print(f"  Failures: {len(failures)}/{len(y_test)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
