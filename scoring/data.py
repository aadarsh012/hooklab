"""Data loading and feature matrix construction for the scoring model."""

import json
import logging
from typing import Dict, List, Tuple

import numpy as np

from embeddings.store import HookVectorStore

logger = logging.getLogger(__name__)


def load_hooks(path: str) -> List[dict]:
    """Read a JSONL file and return a list of hook dicts."""
    hooks = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                hooks.append(json.loads(line))
    return hooks


def build_feature_matrix(
    hooks: List[dict], store: HookVectorStore
) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """Build X (embeddings) and y (labels) arrays from hooks.

    Fetches embeddings from Chroma where available.
    For hooks not in Chroma, embeds on the fly via the SentenceTransformer.

    Returns:
        X: shape (n_hooks, 384) — embedding vectors
        y: shape (n_hooks,) — binary labels (1=strong, 0=weak)
        hook_ids: list of hook IDs in same order
    """
    hook_ids = [h["hook_id"] for h in hooks]

    # Try fetching from Chroma first
    stored = store.get_embeddings(hook_ids)

    X_list = []
    y_list = []
    valid_ids = []

    for h in hooks:
        hid = h["hook_id"]
        label = h.get("label", "")

        if not label:
            logger.warning("Hook %s has no label, skipping", hid)
            continue

        # Get embedding: from Chroma if available, else encode on the fly
        if hid in stored and stored[hid] is not None:
            embedding = stored[hid]
        else:
            logger.info("Hook %s not in Chroma, encoding on the fly", hid)
            embedding = store.model.encode([h["hook_text"]]).tolist()[0]

        X_list.append(embedding)
        y_list.append(1 if label == "strong" else 0)
        valid_ids.append(hid)

    X = np.array(X_list)
    y = np.array(y_list)

    logger.info("Built feature matrix: X=%s, y=%s (strong=%d, weak=%d)",
                X.shape, y.shape, int(y.sum()), int(len(y) - y.sum()))

    return X, y, valid_ids


def load_dataset(
    train_path: str = "data/processed/train.jsonl",
    test_path: str = "data/processed/test.jsonl",
) -> Dict:
    """Load train/test data and build feature matrices.

    Returns dict with keys:
        X_train, y_train, X_test, y_test,
        train_ids, test_ids, train_hooks, test_hooks
    """
    store = HookVectorStore()

    train_hooks = load_hooks(train_path)
    test_hooks = load_hooks(test_path)

    logger.info("Loaded %d train hooks, %d test hooks", len(train_hooks), len(test_hooks))

    X_train, y_train, train_ids = build_feature_matrix(train_hooks, store)
    X_test, y_test, test_ids = build_feature_matrix(test_hooks, store)

    return {
        "X_train": X_train,
        "y_train": y_train,
        "X_test": X_test,
        "y_test": y_test,
        "train_ids": train_ids,
        "test_ids": test_ids,
        "train_hooks": train_hooks,
        "test_hooks": test_hooks,
    }
