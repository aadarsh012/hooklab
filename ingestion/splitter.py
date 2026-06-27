from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from sklearn.model_selection import train_test_split

from ingestion.schemas import CleanedHook, SplitDataset

logger = logging.getLogger(__name__)

LABELED_INPUT_PATH = Path("data/processed/labeled_hooks.jsonl")
TRAIN_OUTPUT_PATH = Path("data/processed/train.jsonl")
TEST_OUTPUT_PATH = Path("data/processed/test.jsonl")
METADATA_OUTPUT_PATH = Path("data/processed/split_metadata.json")


def split_dataset(
    input_path: str | Path | None = None,
    train_path: str | Path | None = None,
    test_path: str | Path | None = None,
    test_size: float = 0.2,
    random_state: int = 42,
) -> SplitDataset:
    """Stratified train/test split. Test set is sacred — don't touch until eval."""
    input_path = Path(input_path or LABELED_INPUT_PATH)
    train_path = Path(train_path or TRAIN_OUTPUT_PATH)
    test_path = Path(test_path or TEST_OUTPUT_PATH)

    hooks = []
    with open(input_path) as f:
        for line in f:
            hooks.append(CleanedHook(**json.loads(line)))

    labels = [h.label.value for h in hooks if h.label is not None]

    train_hooks, test_hooks = train_test_split(
        hooks,
        test_size=test_size,
        random_state=random_state,
        stratify=labels,
    )

    # Save train and test sets
    for path, split in [(train_path, train_hooks), (test_path, test_hooks)]:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            for hook in split:
                f.write(hook.model_dump_json() + "\n")

    # Compute label distributions
    def _dist(split: list[CleanedHook]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for h in split:
            key = h.label.value if h.label else "unlabeled"
            counts[key] = counts.get(key, 0) + 1
        return counts

    metadata = SplitDataset(
        total=len(hooks),
        train_count=len(train_hooks),
        test_count=len(test_hooks),
        label_distribution_train=_dist(train_hooks),
        label_distribution_test=_dist(test_hooks),
        split_date=datetime.now(timezone.utc).isoformat(),
    )

    with open(METADATA_OUTPUT_PATH, "w") as f:
        f.write(metadata.model_dump_json(indent=2))

    logger.info(
        f"Split: {metadata.train_count} train / {metadata.test_count} test "
        f"(from {metadata.total} total)"
    )
    logger.info(f"  Train dist: {metadata.label_distribution_train}")
    logger.info(f"  Test dist:  {metadata.label_distribution_test}")

    return metadata
