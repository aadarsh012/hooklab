"""Save and load trained scoring models."""

import joblib

DEFAULT_MODEL_PATH = "scoring/trained_model.joblib"


def save_model(model: object, path: str = DEFAULT_MODEL_PATH) -> None:
    """Save a trained model to disk."""
    joblib.dump(model, path)


def load_model(path: str = DEFAULT_MODEL_PATH) -> object:
    """Load a trained model from disk.

    Raises:
        FileNotFoundError: If no saved model exists.
    """
    try:
        return joblib.load(path)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"No trained model found at '{path}'. "
            "Run 'python scripts/train_scorer.py' first."
        )
