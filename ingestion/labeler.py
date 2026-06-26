from __future__ import annotations

import json
import logging
import statistics
from pathlib import Path

from ingestion.schemas import CleanedHook, EngagementLabel

logger = logging.getLogger(__name__)

CLEANED_INPUT_PATH = Path("data/processed/cleaned_hooks.jsonl")
LABELED_OUTPUT_PATH = Path("data/processed/labeled_hooks.jsonl")


def label_hooks(
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
    strategy: str = "median",
) -> list[CleanedHook]:
    """
    Assign strong/weak labels based on engagement ratio.

    strategy='median': above median = strong, at or below = weak
    strategy='tercile': top third = strong, bottom third = weak, middle dropped
    """
    input_path = Path(input_path or CLEANED_INPUT_PATH)
    output_path = Path(output_path or LABELED_OUTPUT_PATH)

    hooks = []
    with open(input_path) as f:
        for line in f:
            hooks.append(CleanedHook(**json.loads(line)))

    ratios = [h.engagement_ratio for h in hooks]

    if strategy == "median":
        threshold = statistics.median(ratios)
        labeled = []
        for hook in hooks:
            hook.label = (
                EngagementLabel.STRONG
                if hook.engagement_ratio > threshold
                else EngagementLabel.WEAK
            )
            labeled.append(hook)

    elif strategy == "tercile":
        sorted_ratios = sorted(ratios)
        lower = sorted_ratios[len(sorted_ratios) // 3]
        upper = sorted_ratios[2 * len(sorted_ratios) // 3]
        labeled = []
        for hook in hooks:
            if hook.engagement_ratio >= upper:
                hook.label = EngagementLabel.STRONG
                labeled.append(hook)
            elif hook.engagement_ratio <= lower:
                hook.label = EngagementLabel.WEAK
                labeled.append(hook)
            # Middle third is dropped
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    # Log distribution
    strong = sum(1 for h in labeled if h.label == EngagementLabel.STRONG)
    weak = sum(1 for h in labeled if h.label == EngagementLabel.WEAK)
    logger.info(
        f"Labeling ({strategy}): {len(labeled)} hooks — "
        f"strong={strong}, weak={weak}"
    )
    if strategy == "median":
        logger.info(f"  Median threshold: {threshold:.6f}")
    logger.info(
        f"  Engagement range: {min(ratios):.6f} - {max(ratios):.6f}, "
        f"mean: {statistics.mean(ratios):.6f}"
    )

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for hook in labeled:
            f.write(hook.model_dump_json() + "\n")

    return labeled
