import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from ingestion.schemas import RawHook

logger = logging.getLogger(__name__)

RAW_OUTPUT_PATH = Path("data/raw/raw_hooks.jsonl")


def import_manual_csv(csv_path: str) -> list[RawHook]:
    """
    Import hand-collected hooks from a CSV file.

    Expected columns: hook_text, view_count, like_count
    Optional columns: source, title, video_id
    """
    df = pd.read_csv(csv_path)

    required = {"hook_text", "view_count", "like_count"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")

    RAW_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    hooks = []

    for _, row in df.iterrows():
        hook_text = str(row["hook_text"]).strip()
        if not hook_text or len(hook_text) < 10:
            continue

        video_id = str(row.get("video_id", ""))
        if not video_id or video_id == "nan":
            video_id = hashlib.sha256(hook_text.encode()).hexdigest()[:12]

        raw_hook = RawHook(
            video_id=video_id,
            source=str(row.get("source", "manual")),
            title=str(row.get("title", "")),
            hook_text=hook_text,
            full_transcript_excerpt=hook_text,
            view_count=int(row["view_count"]),
            like_count=int(row["like_count"]),
            collected_at=datetime.now(timezone.utc).isoformat(),
        )

        hooks.append(raw_hook)

        with open(RAW_OUTPUT_PATH, "a") as f:
            f.write(raw_hook.model_dump_json() + "\n")

    logger.info(f"Imported {len(hooks)} hooks from {csv_path}")
    return hooks
