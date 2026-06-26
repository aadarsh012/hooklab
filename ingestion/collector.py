from __future__ import annotations

import json
import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi

from hooklab.config import (
    MAX_RESULTS_PER_QUERY,
    SEARCH_QUERIES,
    TARGET_HOOK_COUNT,
    YOUTUBE_API_KEY,
)
from ingestion.schemas import RawHook

logger = logging.getLogger(__name__)

RAW_OUTPUT_PATH = Path("data/raw/raw_hooks.jsonl")


def _get_youtube_client():
    if not YOUTUBE_API_KEY:
        raise ValueError("YOUTUBE_API_KEY not set in .env")
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


def search_shorts(youtube, query: str, max_results: int = 50) -> list[dict]:
    """Search YouTube for short-form videos matching the query."""
    results = []
    next_page_token = None

    while len(results) < max_results:
        request = youtube.search().list(
            q=query,
            part="id,snippet",
            type="video",
            videoDuration="short",
            relevanceLanguage="en",
            maxResults=min(50, max_results - len(results)),
            pageToken=next_page_token,
        )

        try:
            response = request.execute()
        except HttpError as e:
            if e.resp.status == 403:
                logger.warning("Rate limit hit, waiting 60s...")
                time.sleep(60)
                continue
            raise

        for item in response.get("items", []):
            results.append(
                {
                    "video_id": item["id"]["videoId"],
                    "title": item["snippet"]["title"],
                }
            )

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return results


def get_video_stats(youtube, video_ids: list[str]) -> dict[str, dict]:
    """Batch fetch video statistics."""
    stats = {}

    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        request = youtube.videos().list(
            part="statistics",
            id=",".join(batch),
        )

        try:
            response = request.execute()
        except HttpError as e:
            if e.resp.status == 403:
                logger.warning("Rate limit hit on stats fetch, waiting 60s...")
                time.sleep(60)
                response = request.execute()
            else:
                raise

        for item in response.get("items", []):
            s = item["statistics"]
            stats[item["id"]] = {
                "view_count": int(s.get("viewCount", 0)),
                "like_count": int(s.get("likeCount", 0)),
                "comment_count": int(s.get("commentCount", 0)),
            }

    return stats


def extract_hook_from_transcript(
    video_id: str, max_sentences: int = 2
) -> tuple[str, str] | None:
    """Extract the first 1-2 sentences from a video's auto-captions."""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(["en"])
        segments = transcript.fetch()

        full_text = " ".join(seg.text for seg in segments).strip()

        if len(full_text) < 10:
            return None

        # Check for non-English content (simple heuristic)
        ascii_ratio = sum(1 for c in full_text if ord(c) < 128) / len(full_text)
        if ascii_ratio < 0.7:
            return None

        # Split into sentences and take first N
        sentences = re.split(r"(?<=[.!?])\s+", full_text)
        hook = " ".join(sentences[:max_sentences]).strip()

        # Longer excerpt for debugging context
        excerpt = " ".join(sentences[: max_sentences + 2]).strip()

        if len(hook) < 10:
            return None

        return hook, excerpt

    except Exception:
        return None


def collect_hooks(
    queries: list[str] | None = None,
    max_per_query: int | None = None,
    target_count: int | None = None,
) -> list[RawHook]:
    """
    Main collection orchestrator. Searches YouTube, fetches stats
    and transcripts, saves results to JSONL.
    """
    queries = queries or SEARCH_QUERIES
    max_per_query = max_per_query or MAX_RESULTS_PER_QUERY
    target_count = target_count or TARGET_HOOK_COUNT

    youtube = _get_youtube_client()
    seen_video_ids: set[str] = set()
    hooks: list[RawHook] = []

    # Load existing hooks to avoid re-collecting
    if RAW_OUTPUT_PATH.exists():
        with open(RAW_OUTPUT_PATH) as f:
            for line in f:
                data = json.loads(line)
                seen_video_ids.add(data["video_id"])
        logger.info(f"Loaded {len(seen_video_ids)} existing hooks, resuming...")

    RAW_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    for query in queries:
        if len(hooks) + len(seen_video_ids) >= target_count:
            break

        logger.info(f"Searching: '{query}'...")
        search_results = search_shorts(youtube, query, max_per_query)

        # Filter already-seen videos
        new_results = [r for r in search_results if r["video_id"] not in seen_video_ids]
        if not new_results:
            logger.info(f"  No new videos for '{query}', skipping.")
            continue

        # Fetch stats in batch
        video_ids = [r["video_id"] for r in new_results]
        stats = get_video_stats(youtube, video_ids)

        collected = 0
        skipped = 0

        for result in new_results:
            vid = result["video_id"]
            if vid in seen_video_ids:
                continue

            seen_video_ids.add(vid)
            video_stats = stats.get(vid)
            if not video_stats:
                skipped += 1
                continue

            hook_result = extract_hook_from_transcript(vid)
            if not hook_result:
                skipped += 1
                continue

            hook_text, excerpt = hook_result

            raw_hook = RawHook(
                video_id=vid,
                source="youtube",
                title=result["title"],
                hook_text=hook_text,
                full_transcript_excerpt=excerpt,
                view_count=video_stats["view_count"],
                like_count=video_stats["like_count"],
                comment_count=video_stats["comment_count"],
                collected_at=datetime.now(timezone.utc).isoformat(),
            )

            hooks.append(raw_hook)
            collected += 1

            # Save incrementally
            with open(RAW_OUTPUT_PATH, "a") as f:
                f.write(raw_hook.model_dump_json() + "\n")

        logger.info(
            f"  '{query}': collected {collected}, skipped {skipped} "
            f"(total: {len(hooks) + len(seen_video_ids) - len(hooks)})"
        )

    logger.info(
        f"Collection complete. {len(hooks)} new hooks collected. "
        f"Total in file: {len(hooks) + len(seen_video_ids) - len(hooks)}"
    )
    return hooks
