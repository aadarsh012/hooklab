"""Pydantic schemas for the LangGraph agent pipeline."""

from typing import List, Optional

from pydantic import BaseModel

from ingestion.schemas import EngagementLabel


class DimensionScore(BaseModel):
    """Score for a single scoring dimension (1-10)."""

    dimension: str  # e.g. "specificity"
    score: int  # 1-10
    explanation: str


class ScoreBreakdown(BaseModel):
    """Combined ML prediction + LLM dimension analysis."""

    label: EngagementLabel
    confidence: float
    dimension_scores: List[DimensionScore]


class SimilarHook(BaseModel):
    """A similar hook retrieved from the corpus (for grounding)."""

    hook_text: str
    label: Optional[str] = None
    engagement_ratio: float = 0.0
    distance: float = 0.0


class PersonaReaction(BaseModel):
    """A synthetic viewer's reaction to the hook."""

    persona_name: str
    would_watch: bool
    reaction: str
    reasoning: str


class HookRewrite(BaseModel):
    """An improved variant of the original hook."""

    rewritten_hook: str
    changes_made: str
    target_dimension: str  # which weak dimension this targets


class AnalysisResult(BaseModel):
    """The top-level output of analyze(hook)."""

    hook_text: str
    score_breakdown: ScoreBreakdown
    similar_hooks: List[SimilarHook]
    persona_reactions: List[PersonaReaction]
    rewrites: List[HookRewrite]


class PipelineState(BaseModel):
    """LangGraph shared state flowing through all nodes."""

    hook_text: str
    score_breakdown: Optional[ScoreBreakdown] = None
    similar_hooks: List[SimilarHook] = []
    persona_reactions: List[PersonaReaction] = []
    rewrites: List[HookRewrite] = []
