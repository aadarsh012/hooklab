"""
Analyze a hook through the full LangGraph pipeline.

Usage:
    python scripts/analyze_hook.py "Stop doing crunches if you want abs"
    python scripts/analyze_hook.py "Full body workout at home"
"""

import logging
import sys

sys.path.insert(0, ".")

from agents.pipeline import analyze

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/analyze_hook.py \"your hook text here\"")
        return

    hook_text = sys.argv[1]
    print(f"\nAnalyzing: \"{hook_text}\"")
    print("=" * 70)

    result = analyze(hook_text)

    # Score breakdown
    sb = result.score_breakdown
    print(f"\n--- SCORE ---")
    print(f"ML Prediction: {sb.label.value.upper()} ({sb.confidence:.0%} confidence)")
    print(f"\nDimension Scores:")
    for d in sb.dimension_scores:
        bar = "█" * d.score + "░" * (10 - d.score)
        print(f"  {d.dimension:<20s} [{bar}] {d.score}/10")
        print(f"    {d.explanation}")

    # Similar hooks
    if result.similar_hooks:
        print(f"\n--- SIMILAR HOOKS ---")
        for i, h in enumerate(result.similar_hooks[:3], 1):
            print(f"  {i}. [{h.label}] \"{h.hook_text}\"")

    # Persona reactions
    if result.persona_reactions:
        print(f"\n--- PERSONA REACTIONS ---")
        for r in result.persona_reactions:
            icon = "👍" if r.would_watch else "👎"
            print(f"\n  {icon} {r.persona_name}")
            print(f"    Reaction: {r.reaction}")
            print(f"    Reasoning: {r.reasoning}")

    # Rewrites
    if result.rewrites:
        print(f"\n--- REWRITES ---")
        for i, rw in enumerate(result.rewrites, 1):
            print(f"\n  Variant {chr(64 + i)}: \"{rw.rewritten_hook}\"")
            print(f"    Changes: {rw.changes_made}")
            print(f"    Targets: {rw.target_dimension}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
