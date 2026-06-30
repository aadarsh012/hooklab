from __future__ import annotations

import hashlib
import html
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
# Hashtags (e.g. #fitness #shorts)
HASHTAGS = re.compile(r"#\S+")
# Emojis (broad Unicode range)
EMOJIS = re.compile(
    r"[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0000FE00-\U0000FE0F"
    r"\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0"
    r"\U0000200D\U0000FE0F]+",
    re.UNICODE,
)
# Pipe separators used in titles (e.g. "Title | #shorts")
PIPE_SUFFIX = re.compile(r"\s*\|.*$")
# HTML entities
HTML_ENTITIES = re.compile(r"&#?\w+;")
# Promotional/meta phrases in titles
META_PHRASES = re.compile(
    r"(?:viral|trending|viralvideo|ytshorts|youtubeshorts|shortvideo|shortsviral|"
    r"shortsfeed|reels|reelsinstagram|yt)\b",
    re.IGNORECASE,
)

MIN_VIEW_COUNT = 100
MIN_HOOK_LENGTH = 15  # Increased from 10 — short hooks are usually junk
MIN_WORD_COUNT = 3    # At least 3 real words


def normalize_title(title: str) -> str:
    """Clean a YouTube title into a usable hook."""
    text = html.unescape(title)         # &#39; -> '
    text = HASHTAGS.sub("", text)        # Remove #fitness #shorts etc
    text = EMOJIS.sub("", text)          # Remove emojis
    text = PIPE_SUFFIX.sub("", text)     # Remove "| Channel Name" suffixes
    text = META_PHRASES.sub("", text)    # Remove "viral", "trending" etc
    text = re.sub(r"\s+", " ", text).strip()
    # Remove trailing/leading punctuation junk
    text = text.strip("-–—|:,. ")
    return text


def normalize_transcript(text: str) -> str:
    """Clean transcript text: remove artifacts, filler words, collapse whitespace."""
    text = ARTIFACTS.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = FILLER_START.sub("", text)
    return text.strip()


def _is_junk_transcript(text: str) -> bool:
    """Check if a transcript is too noisy to use as a hook."""
    cleaned = ARTIFACTS.sub("", text).strip()
    # Too short after removing artifacts
    if len(cleaned) < 10:
        return True
    # Mostly non-words (single chars, gibberish)
    words = cleaned.split()
    real_words = [w for w in words if len(w) > 1]
    if len(real_words) < 3:
        return True
    return False


def _pick_best_hook(raw: dict) -> str:
    """Choose the best hook text from transcript or title.

    Priority:
    1. Good transcript (actual spoken words) -> use transcript
    2. Junk transcript -> clean the title and use that
    3. No transcript -> clean the title and use that
    """
    transcript = raw.get("hook_text", "").strip()
    title = raw.get("title", "").strip()

    # If transcript looks real, use it
    if transcript and not _is_junk_transcript(transcript):
        return normalize_transcript(transcript)

    # Fall back to cleaned title
    if title:
        return normalize_title(title)

    # Last resort: try the transcript anyway
    return normalize_transcript(transcript) if transcript else ""


def _hook_id(text: str) -> str:
    """Deterministic ID from normalized lowercase text."""
    return hashlib.sha256(text.lower().strip().encode()).hexdigest()[:16]


def _is_only_hashtags_or_meta(text: str) -> bool:
    """Check if text is just hashtags/meta with no real content."""
    stripped = HASHTAGS.sub("", text).strip()
    stripped = EMOJIS.sub("", stripped).strip()
    stripped = META_PHRASES.sub("", stripped).strip()
    stripped = stripped.strip("-–—|:,. ")
    return len(stripped) < 5


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
    2. Pick best hook text (transcript vs title)
    3. Filter by min views, min text length, min word count
    4. Filter out non-English and hashtag-only content
    5. Deduplicate by hook_id
    6. Compute engagement ratio
    7. Save cleaned output
    """
    input_path = Path(input_path or RAW_INPUT_PATH)
    output_path = Path(output_path or CLEANED_OUTPUT_PATH)

    # Load raw hooks
    raw_hooks = []
    with open(input_path) as f:
        for line in f:
            line = line.strip()
            if line:
                raw_hooks.append(json.loads(line))

    initial_count = len(raw_hooks)
    logger.info(f"Loaded {initial_count} raw hooks")

    cleaned = []
    filtered_count = 0
    filter_reasons: dict[str, int] = {}

    for raw in raw_hooks:
        # Filter: minimum views
        if raw["view_count"] < MIN_VIEW_COUNT:
            filtered_count += 1
            filter_reasons["low_views"] = filter_reasons.get("low_views", 0) + 1
            continue

        # Pick best hook text
        hook_text = _pick_best_hook(raw)

        # Filter: only hashtags/meta
        if _is_only_hashtags_or_meta(hook_text):
            filtered_count += 1
            filter_reasons["hashtags_only"] = filter_reasons.get("hashtags_only", 0) + 1
            continue

        # Filter: minimum length after normalization
        if len(hook_text) < MIN_HOOK_LENGTH:
            filtered_count += 1
            filter_reasons["too_short"] = filter_reasons.get("too_short", 0) + 1
            continue

        # Filter: minimum word count
        words = hook_text.split()
        if len(words) < MIN_WORD_COUNT:
            filtered_count += 1
            filter_reasons["too_few_words"] = filter_reasons.get("too_few_words", 0) + 1
            continue

        # Filter: non-English (>30% non-ASCII)
        ascii_ratio = sum(1 for c in hook_text if ord(c) < 128) / max(len(hook_text), 1)
        if ascii_ratio < 0.7:
            filtered_count += 1
            filter_reasons["non_english"] = filter_reasons.get("non_english", 0) + 1
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

    logger.info(f"Filtered out {filtered_count} hooks: {filter_reasons}")

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
