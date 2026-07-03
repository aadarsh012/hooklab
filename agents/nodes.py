"""LangGraph node functions for the hook analysis pipeline."""

import json
import logging
import re
from typing import Any, Dict

from agents.llm import call_llm
from agents.schemas import (
    DimensionScore,
    HookRewrite,
    PersonaReaction,
    PipelineState,
    ScoreBreakdown,
    SimilarHook,
)
from config.config import SCORING_DIMENSIONS
from config.system_prompt import HOOK_EXPERT_SYSTEM_PROMPT
from embeddings.store import HookVectorStore
from scoring.classifier import predict_strength

logger = logging.getLogger(__name__)


# --- Persona definitions ---

PERSONAS = [
    {
        "name": "Curious Beginner",
        "backstory": (
            "I just started going to the gym 2 months ago. I scroll through fitness "
            "Shorts looking for quick tips and motivation. I don't know much about "
            "exercise science, so I'm drawn to simple, clear advice. Clickbait "
            "frustrates me if it doesn't deliver."
        ),
    },
    {
        "name": "Skeptical Trainer",
        "backstory": (
            "I'm a certified personal trainer with 10 years of experience. I've seen "
            "every clickbait trick in the book. I value accuracy and evidence-based "
            "advice. I'll stop scrolling only if the hook promises something genuinely "
            "useful or challenges a real misconception."
        ),
    },
    {
        "name": "Content Creator",
        "backstory": (
            "I run a 500K fitness account on TikTok and YouTube Shorts. I know what "
            "gets views and what falls flat. I analyze hooks professionally — I'm "
            "looking at structure, curiosity gap, and whether this would perform "
            "well with the algorithm."
        ),
    },
]


# --- Node functions ---


def scorer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Score the hook: ML prediction + LLM dimension breakdown."""
    hook_text = state["hook_text"]

    # 1. ML prediction
    prediction = predict_strength(hook_text)
    logger.info("ML prediction: %s (%.0f%%)", prediction.label.value, prediction.confidence * 100)

    # 2. LLM dimension scores
    dimensions_str = ", ".join(SCORING_DIMENSIONS)
    prompt = (
        f'Analyze this fitness hook: "{hook_text}"\n\n'
        f"Score it on these 4 dimensions (1-10 each): {dimensions_str}\n\n"
        "Respond in this exact JSON format, nothing else:\n"
        "[\n"
        '  {"dimension": "specificity", "score": <1-10>, "explanation": "<1 sentence>"},\n'
        '  {"dimension": "curiosity_gap", "score": <1-10>, "explanation": "<1 sentence>"},\n'
        '  {"dimension": "clarity_of_payoff", "score": <1-10>, "explanation": "<1 sentence>"},\n'
        '  {"dimension": "concreteness", "score": <1-10>, "explanation": "<1 sentence>"}\n'
        "]"
    )

    llm_response = call_llm(HOOK_EXPERT_SYSTEM_PROMPT, prompt)

    # Parse JSON from response
    dimension_scores = _parse_dimension_scores(llm_response)

    score_breakdown = ScoreBreakdown(
        label=prediction.label,
        confidence=prediction.confidence,
        dimension_scores=dimension_scores,
    )

    return {"score_breakdown": score_breakdown}


def retriever_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve similar hooks from the corpus for grounding."""
    hook_text = state["hook_text"]

    store = HookVectorStore()
    results = store.retrieve(hook_text, top_k=5)

    similar_hooks = [
        SimilarHook(
            hook_text=r.hook_text,
            label=r.label,
            engagement_ratio=r.engagement_ratio,
            distance=r.distance,
        )
        for r in results
    ]

    logger.info("Retrieved %d similar hooks", len(similar_hooks))
    return {"similar_hooks": similar_hooks}


def persona_beginner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Curious Beginner persona reaction."""
    return _run_persona(state, PERSONAS[0])


def persona_trainer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Skeptical Trainer persona reaction."""
    return _run_persona(state, PERSONAS[1])


def persona_creator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Content Creator persona reaction."""
    return _run_persona(state, PERSONAS[2])


def rewriter_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Rewrite the hook in 2 improved variants."""
    hook_text = state["hook_text"]
    score_breakdown = state.get("score_breakdown")
    similar_hooks = state.get("similar_hooks", [])
    persona_reactions = state.get("persona_reactions", [])

    # Find weakest dimensions
    weak_dims = []
    if score_breakdown and score_breakdown.dimension_scores:
        sorted_dims = sorted(score_breakdown.dimension_scores, key=lambda d: d.score)
        weak_dims = [d.dimension for d in sorted_dims[:2]]

    # Build grounding context
    strong_examples = [h for h in similar_hooks if h.label == "strong"]
    examples_str = "\n".join(
        f"- \"{h.hook_text}\" (engagement: {h.engagement_ratio:.4f})"
        for h in strong_examples[:3]
    )

    # Build persona feedback summary
    feedback_str = "\n".join(
        f"- {r.persona_name}: {'Would watch' if r.would_watch else 'Would skip'} — {r.reasoning}"
        for r in persona_reactions
    )

    prompt = (
        f'Original hook: "{hook_text}"\n\n'
        f"Weakest dimensions: {', '.join(weak_dims) if weak_dims else 'unknown'}\n\n"
        f"Strong hooks from the corpus for reference:\n{examples_str}\n\n"
        f"Persona feedback:\n{feedback_str}\n\n"
        "Write exactly 2 improved variants of this hook.\n"
        "Variant A: Improve the weakest dimension while keeping the same angle.\n"
        "Variant B: Take a completely different hook formula.\n\n"
        "Respond in this exact JSON format, nothing else:\n"
        "[\n"
        '  {"rewritten_hook": "<variant A>", "changes_made": "<1 sentence>", "target_dimension": "<dimension>"},\n'
        '  {"rewritten_hook": "<variant B>", "changes_made": "<1 sentence>", "target_dimension": "<dimension>"}\n'
        "]"
    )

    llm_response = call_llm(HOOK_EXPERT_SYSTEM_PROMPT, prompt)
    rewrites = _parse_rewrites(llm_response)

    logger.info("Generated %d rewrites", len(rewrites))
    return {"rewrites": rewrites}


# --- Internal helpers ---


def _run_persona(state: Dict[str, Any], persona: dict) -> Dict[str, Any]:
    """Run a single persona reaction."""
    hook_text = state["hook_text"]
    score_breakdown = state.get("score_breakdown")
    similar_hooks = state.get("similar_hooks", [])

    # Build score context
    score_ctx = ""
    if score_breakdown:
        scores_str = ", ".join(
            f"{d.dimension}: {d.score}/10" for d in score_breakdown.dimension_scores
        )
        score_ctx = f"\nScoring: {score_breakdown.label.value} ({score_breakdown.confidence:.0%}). Dimensions: {scores_str}"

    # Build similar hooks context
    similar_ctx = ""
    if similar_hooks:
        similar_ctx = "\nSimilar hooks from the corpus:\n" + "\n".join(
            f"- \"{h.hook_text}\" [{h.label}]" for h in similar_hooks[:3]
        )

    system = (
        f"You are {persona['name']}. {persona['backstory']}\n"
        "You are scrolling through fitness Shorts on your phone."
    )

    prompt = (
        f'You see this hook: "{hook_text}"\n'
        f"{score_ctx}\n{similar_ctx}\n\n"
        "Would you stop scrolling and watch? Answer in this exact JSON format, nothing else:\n"
        "{\n"
        f'  "persona_name": "{persona["name"]}",\n'
        '  "would_watch": <true or false>,\n'
        '  "reaction": "<your gut reaction in 1-2 sentences, in character>",\n'
        '  "reasoning": "<why you would or wouldn\'t watch, reference a similar hook if relevant>"\n'
        "}"
    )

    llm_response = call_llm(system, prompt)
    reaction = _parse_persona_reaction(llm_response, persona["name"])

    logger.info("Persona '%s': would_watch=%s", persona["name"], reaction.would_watch)

    # Append to existing reactions
    existing = list(state.get("persona_reactions", []))
    existing.append(reaction)
    return {"persona_reactions": existing}


def _extract_json(text: str) -> str:
    """Extract JSON from LLM response (handles markdown code blocks)."""
    # Try to find JSON in code blocks
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()

    # Try to find raw JSON array or object
    for start, end in [("[", "]"), ("{", "}")]:
        idx_start = text.find(start)
        idx_end = text.rfind(end)
        if idx_start != -1 and idx_end > idx_start:
            return text[idx_start : idx_end + 1]

    return text.strip()


def _parse_dimension_scores(response: str) -> list:
    """Parse LLM response into DimensionScore objects."""
    try:
        raw = json.loads(_extract_json(response))
        return [
            DimensionScore(
                dimension=item.get("dimension", "unknown"),
                score=max(1, min(10, int(item.get("score", 5)))),
                explanation=item.get("explanation", ""),
            )
            for item in raw
        ]
    except (json.JSONDecodeError, TypeError, KeyError) as e:
        logger.warning("Failed to parse dimension scores: %s", e)
        # Return default scores
        return [
            DimensionScore(dimension=d, score=5, explanation="Could not parse LLM response")
            for d in SCORING_DIMENSIONS
        ]


def _parse_persona_reaction(response: str, persona_name: str) -> PersonaReaction:
    """Parse LLM response into PersonaReaction."""
    try:
        raw = json.loads(_extract_json(response))
        return PersonaReaction(
            persona_name=raw.get("persona_name", persona_name),
            would_watch=bool(raw.get("would_watch", False)),
            reaction=raw.get("reaction", ""),
            reasoning=raw.get("reasoning", ""),
        )
    except (json.JSONDecodeError, TypeError, KeyError) as e:
        logger.warning("Failed to parse persona reaction: %s", e)
        return PersonaReaction(
            persona_name=persona_name,
            would_watch=False,
            reaction="Could not parse LLM response",
            reasoning=str(e),
        )


def _parse_rewrites(response: str) -> list:
    """Parse LLM response into HookRewrite objects."""
    try:
        raw = json.loads(_extract_json(response))
        return [
            HookRewrite(
                rewritten_hook=item.get("rewritten_hook", ""),
                changes_made=item.get("changes_made", ""),
                target_dimension=item.get("target_dimension", ""),
            )
            for item in raw
        ]
    except (json.JSONDecodeError, TypeError, KeyError) as e:
        logger.warning("Failed to parse rewrites: %s", e)
        return []
