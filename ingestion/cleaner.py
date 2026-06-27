from __future__ import annotations

import hashlib
import json
import logging
import re
from pathlib import Path

from ingestion.schemas import CleanedHook

logger = logging.getLogger(__name__)

RAW_INPUT_PATH = Path("data/raw/raw_hooks.jsonl")
CLEANED_OUTPUT_PATH = Path("data/processed/cleaned_hooks.jsonl")

# Transcript artifacts to remove
ARTIFACTS = re.compile(r"\[(?:Music|Applause|Laughter|Cheering|Foreign)\]", re.IGNORECASE)
# Common filler words at the start
FILLER_START = re.compile(r"^(?:um|uh|so|okay so|ok so|alright so|like|you know)\s+", re.IGNORECASE)

MIN_VIEW_COUNT = 100
MIN_HOOK_LENGTH = 10


def normalize_text(text: str) -> str:
    """Normalize hook text: remove artifacts, filler words, collapse whitespace."""
    text = ARTIFACTS.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = FILLER_START.sub("", text)
    return text.strip()


def _hook_id(text: str) -> str:
    """Deterministic ID from normalized lowercase text."""
    return hashlib.sha256(text.lower().strip().encode()).hexdigest()[:16]


def deduplicate(hooks: list[dict]) -> list[dict]:
    """Keep the hook with the highest view_count for each unique hook_id."""
    best: dict[str, dict] = {}
    for hook in hooks:
        hid = hook["hook_id"]
        if hid not in best or hook["view_count"] > best[hid]["view_count"]:
            best[hid] = hook
    return list(best.values())


def clean_hooks(
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> list[CleanedHook]:
    """
    Full cleaning pipeline:
    1. Load raw hooks
    2. Filter by min views and min text length
    3. Normalize text
    4. Deduplicate by hook_id
    5. Compute engagement ratio
    6. Save cleaned output
    """
    input_path = Path(input_path or RAW_INPUT_PATH)
    output_path = Path(output_path or CLEANED_OUTPUT_PATH)

    # Load raw hooks
    raw_hooks = []
    with open(input_path) as f:
        for line in f:
            raw_hooks.append(json.loads(line))

    initial_count = len(raw_hooks)
    logger.info(f"Loaded {initial_count} raw hooks")

    cleaned = []
    filtered_count = 0

    for raw in raw_hooks:
        # Filter: minimum views
        if raw["view_count"] < MIN_VIEW_COUNT:
            filtered_count += 1
            continue

        # Normalize text
        hook_text = normalize_text(raw["hook_text"])

        # Filter: minimum length after normalization
        if len(hook_text) < MIN_HOOK_LENGTH:
            filtered_count += 1
            continue

        # Filter: non-English (>30% non-ASCII)
        ascii_ratio = sum(1 for c in hook_text if ord(c) < 128) / max(len(hook_text), 1)
        if ascii_ratio < 0.7:
            filtered_count += 1
            continue

        engagement_ratio = raw["like_count"] / raw["view_count"] if raw["view_count"] > 0 else 0.0

        cleaned.append(
            {
                "hook_id": _hook_id(hook_text),
                "video_id": raw["video_id"],
                "source": raw.get("source", "youtube"),
                "hook_text": hook_text,
                "niche": raw.get("niche", "fitness"),
                "view_count": raw["view_count"],
                "like_count": raw["like_count"],
                "engagement_ratio": round(engagement_ratio, 6),
                "label": None,
            }
        )

    logger.info(f"Filtered out {filtered_count} hooks")

    # Deduplicate
    before_dedup = len(cleaned)
    cleaned = deduplicate(cleaned)
    logger.info(f"Removed {before_dedup - len(cleaned)} duplicates")

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results = []
    with open(output_path, "w") as f:
        for hook_data in cleaned:
            hook = CleanedHook(**hook_data)
            f.write(hook.model_dump_json() + "\n")
            results.append(hook)

    logger.info(
        f"Cleaning complete: {initial_count} raw -> {len(results)} cleaned "
        f"(filtered {filtered_count}, deduped {before_dedup - len(cleaned)})"
    )
    return results
