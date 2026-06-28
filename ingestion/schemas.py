from enum import Enum
from typing import Optional

from pydantic import BaseModel


class EngagementLabel(str, Enum):
    STRONG = "strong"
    WEAK = "weak"


class RawHook(BaseModel):
    """Raw data as it comes out of the collector."""

    video_id: str
    source: str = "youtube"
    title: str = ""
    hook_text: str
    full_transcript_excerpt: str = ""
    view_count: int
    like_count: int
    comment_count: Optional[int] = None
    niche: str = "fitness"
    collected_at: str  # ISO timestamp


class CleanedHook(BaseModel):
    """Data after cleaning and deduplication."""

    hook_id: str  # SHA-256 hash of normalized hook_text
    video_id: str
    source: str
    hook_text: str
    niche: str
    view_count: int
    like_count: int
    engagement_ratio: float  # like_count / view_count
    label: Optional[EngagementLabel] = None


class RetrievalResult(BaseModel):
    """A single hook returned from vector similarity search."""

    hook_id: str
    hook_text: str
    label: Optional[str] = None
    engagement_ratio: float = 0.0
    distance: float = 0.0


class SplitDataset(BaseModel):
    """Metadata about the train/test split."""

    total: int
    train_count: int
    test_count: int
    label_distribution_train: dict
    label_distribution_test: dict
    split_date: str
