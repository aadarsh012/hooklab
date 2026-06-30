"""Baselines, classifiers, and the predict_strength public API."""

import logging
from typing import List, Optional

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score

from embeddings.store import HookVectorStore
from ingestion.schemas import EngagementLabel
from scoring.persist import load_model
from scoring.schemas import (
    BaselineResult,
    HookPredictionDetail,
    ModelMetrics,
    PredictionResult,
)

logger = logging.getLogger(__name__)

LABEL_NAMES = ["weak", "strong"]


# --- Baselines ---


def majority_class_baseline(y_train: np.ndarray, y_test: np.ndarray) -> BaselineResult:
    """Always predict the majority class from training set."""
    majority = int(np.bincount(y_train).argmax())
    predictions = [LABEL_NAMES[majority]] * len(y_test)
    y_pred = np.full_like(y_test, majority)

    return BaselineResult(
        name="majority_class",
        accuracy=accuracy_score(y_test, y_pred),
        precision=precision_score(y_test, y_pred, zero_division=0),
        recall=recall_score(y_test, y_pred, zero_division=0),
        predictions=predictions,
    )


def hook_length_baseline(
    train_hooks: List[dict],
    test_hooks: List[dict],
    y_train: np.ndarray,
    y_test: np.ndarray,
) -> BaselineResult:
    """Predict based on hook text character length.

    Computes median length of strong vs weak hooks in training set.
    If a test hook's length is closer to the strong median, predict strong.
    """
    strong_lengths = [len(h["hook_text"]) for h, y in zip(train_hooks, y_train) if y == 1]
    weak_lengths = [len(h["hook_text"]) for h, y in zip(train_hooks, y_train) if y == 0]

    strong_median = np.median(strong_lengths) if strong_lengths else 0
    weak_median = np.median(weak_lengths) if weak_lengths else 0
    threshold = (strong_median + weak_median) / 2

    y_pred = []
    predictions = []
    for h in test_hooks:
        length = len(h["hook_text"])
        # Predict whichever class median is closer
        if abs(length - strong_median) <= abs(length - weak_median):
            y_pred.append(1)
            predictions.append("strong")
        else:
            y_pred.append(0)
            predictions.append("weak")

    y_pred_arr = np.array(y_pred)

    return BaselineResult(
        name="hook_length",
        accuracy=accuracy_score(y_test, y_pred_arr),
        precision=precision_score(y_test, y_pred_arr, zero_division=0),
        recall=recall_score(y_test, y_pred_arr, zero_division=0),
        predictions=predictions,
    )


# --- Models ---


def train_logistic(X_train: np.ndarray, y_train: np.ndarray) -> LogisticRegression:
    """Train a logistic regression on embeddings."""
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train, y_train)
    return model


def train_gradient_boosting(X_train: np.ndarray, y_train: np.ndarray) -> GradientBoostingClassifier:
    """Train a gradient boosting classifier on embeddings."""
    model = GradientBoostingClassifier(n_estimators=50, max_depth=3, random_state=42)
    model.fit(X_train, y_train)
    return model


# --- Evaluation ---


def evaluate_model(
    model,
    X_test: np.ndarray,
    y_test: np.ndarray,
    test_hooks: List[dict],
    test_ids: List[str],
    model_name: str,
) -> ModelMetrics:
    """Evaluate a trained model on the test set."""
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)

    # Per-hook prediction details
    predictions = []
    for i, (hid, hook) in enumerate(zip(test_ids, test_hooks)):
        pred_label = LABEL_NAMES[y_pred[i]]
        true_label = LABEL_NAMES[y_test[i]]
        confidence = float(y_proba[i][y_pred[i]])

        predictions.append(HookPredictionDetail(
            hook_id=hid,
            hook_text=hook["hook_text"],
            true_label=true_label,
            predicted_label=pred_label,
            confidence=confidence,
        ))

    cm = confusion_matrix(y_test, y_pred).tolist()

    return ModelMetrics(
        model_name=model_name,
        accuracy=accuracy_score(y_test, y_pred),
        precision=precision_score(y_test, y_pred, zero_division=0),
        recall=recall_score(y_test, y_pred, zero_division=0),
        confusion_matrix=cm,
        test_predictions=predictions,
    )


# --- Public API ---


def predict_strength(
    hook_text: str,
    model: Optional[object] = None,
    store: Optional[HookVectorStore] = None,
) -> PredictionResult:
    """Predict whether a hook is strong or weak.

    Args:
        hook_text: The hook to classify.
        model: A trained sklearn model. If None, loads from disk.
        store: A HookVectorStore instance. If None, creates a default one.

    Returns:
        PredictionResult with label and confidence.
    """
    if store is None:
        store = HookVectorStore()

    if model is None:
        model = load_model()

    # Embed the hook on the fly
    embedding = store.model.encode([hook_text]).tolist()
    X = np.array(embedding)

    y_pred = model.predict(X)[0]
    y_proba = model.predict_proba(X)[0]
    confidence = float(y_proba[y_pred])
    label = EngagementLabel.STRONG if y_pred == 1 else EngagementLabel.WEAK

    return PredictionResult(
        hook_text=hook_text,
        label=label,
        confidence=confidence,
    )
