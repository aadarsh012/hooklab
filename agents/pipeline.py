"""LangGraph pipeline assembly and the analyze() public API."""

import logging
from typing import Annotated, List, Optional

from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from agents.nodes import (
    persona_beginner_node,
    persona_creator_node,
    persona_trainer_node,
    retriever_node,
    rewriter_node,
    scorer_node,
)
from agents.schemas import (
    AnalysisResult,
    HookRewrite,
    PersonaReaction,
    ScoreBreakdown,
    SimilarHook,
)

logger = logging.getLogger(__name__)


def _merge_reactions(left: list, right: list) -> list:
    """Merge persona reactions from parallel nodes."""
    return left + right


class GraphState(TypedDict, total=False):
    """Typed state for the LangGraph pipeline."""

    hook_text: str
    score_breakdown: Optional[ScoreBreakdown]
    similar_hooks: List[SimilarHook]
    persona_reactions: Annotated[List[PersonaReaction], _merge_reactions]
    rewrites: List[HookRewrite]


def build_graph() -> StateGraph:
    """Build and compile the hook analysis LangGraph."""
    graph = StateGraph(GraphState)

    # Add nodes
    graph.add_node("scorer", scorer_node)
    graph.add_node("retriever", retriever_node)
    graph.add_node("persona_beginner", persona_beginner_node)
    graph.add_node("persona_trainer", persona_trainer_node)
    graph.add_node("persona_creator", persona_creator_node)
    graph.add_node("rewriter", rewriter_node)

    # Define edges: scorer & retriever run first (parallel-safe)
    graph.add_edge(START, "scorer")
    graph.add_edge(START, "retriever")

    # After both scorer and retriever complete, run personas
    graph.add_edge("scorer", "persona_beginner")
    graph.add_edge("scorer", "persona_trainer")
    graph.add_edge("scorer", "persona_creator")
    graph.add_edge("retriever", "persona_beginner")
    graph.add_edge("retriever", "persona_trainer")
    graph.add_edge("retriever", "persona_creator")

    # After all personas complete, run rewriter
    graph.add_edge("persona_beginner", "rewriter")
    graph.add_edge("persona_trainer", "rewriter")
    graph.add_edge("persona_creator", "rewriter")

    # Rewriter is the final node
    graph.add_edge("rewriter", END)

    return graph.compile()


# Compile once at module level
_compiled_graph = None


def _get_graph():
    """Lazy-load the compiled graph."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


def analyze(hook_text: str) -> AnalysisResult:
    """Analyze a hook through the full pipeline.

    This is the public API — the deliverable for Phase 4.

    Args:
        hook_text: The hook to analyze.

    Returns:
        AnalysisResult with scores, persona reactions, and rewrites.
    """
    logger.info("Analyzing hook: '%s'", hook_text[:60])

    graph = _get_graph()
    result = graph.invoke({"hook_text": hook_text})

    return AnalysisResult(
        hook_text=hook_text,
        score_breakdown=result["score_breakdown"],
        similar_hooks=result.get("similar_hooks", []),
        persona_reactions=result.get("persona_reactions", []),
        rewrites=result.get("rewrites", []),
    )
