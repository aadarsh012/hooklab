"""
Run the full evaluation harness.

Usage:
    python scripts/run_eval.py                  # Full eval (includes rewriter, slow)
    python scripts/run_eval.py --skip-rewrites   # Skip rewriter eval (fast)
"""

import logging
import sys
from datetime import datetime, timezone

sys.path.insert(0, ".")

from eval.harness import (
    evaluate_predictions,
    evaluate_rewrites,
    predicted_vs_actual,
    score_rewrites,
)
from eval.report_harness import generate_eval_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def main():
    skip_rewrites = "--skip-rewrites" in sys.argv

    # 1. ML predictions on test set
    logger.info("=== Step 1: ML Predictions ===")
    prediction_data = evaluate_predictions()

    # 2. Predicted vs actual analysis
    logger.info("=== Step 2: Predicted vs Actual ===")
    pva_data = predicted_vs_actual(prediction_data)

    overconfident = pva_data["overconfident_wrong"]
    underconfident = pva_data["underconfident_correct"]
    logger.info("  Overconfident wrong: %d hooks", len(overconfident))
    logger.info("  Underconfident correct: %d hooks", len(underconfident))

    # 3 & 4. Rewriter evaluation
    rewrite_data = {"preference_rate": 0, "total_judgments": 0, "rewrite_wins": 0, "judgments": []}
    rewrite_scores_data = {"upgrade_rate": 0, "upgrades": 0, "total": 0, "scored": []}

    if not skip_rewrites:
        logger.info("=== Step 3: Rewriter Evaluation (LLM-as-judge) ===")
        rewrite_data = evaluate_rewrites(n=20)

        logger.info("=== Step 4: Score Rewrites with Classifier ===")
        rewrite_scores_data = score_rewrites(rewrite_data)
    else:
        logger.info("=== Skipping rewriter evaluation (--skip-rewrites) ===")

    # 5. Generate report
    logger.info("=== Step 5: Generating Report ===")
    generated_at = datetime.now(timezone.utc).isoformat()
    generate_eval_report(
        prediction_data=prediction_data,
        pva_data=pva_data,
        rewrite_data=rewrite_data,
        rewrite_scores=rewrite_scores_data,
        generated_at=generated_at,
    )
    logger.info("Report saved to eval/REPORT.md")

    # Summary
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"  ML Accuracy:     {prediction_data['accuracy']:.2%} ({prediction_data['correct']}/{prediction_data['total']})")
    print(f"  Precision:       {prediction_data['precision']:.2%}")
    print(f"  Recall:          {prediction_data['recall']:.2%}")
    print(f"  F1:              {prediction_data['f1']:.2%}")
    print(f"  Overconfident:   {len(overconfident)} hooks (wrong + >80% confidence)")
    print(f"  Underconfident:  {len(underconfident)} hooks (right + <60% confidence)")

    if not skip_rewrites:
        print(f"\n  Rewrite preference: {rewrite_data['preference_rate']:.0%} "
              f"({rewrite_data['rewrite_wins']}/{rewrite_data['total_judgments']} judge prefers rewrite)")
        print(f"  Upgrade rate:       {rewrite_scores_data['upgrade_rate']:.0%} "
              f"({rewrite_scores_data['upgrades']}/{rewrite_scores_data['total']} "
              f"rewrites classified as strong)")
    else:
        print("\n  Rewriter evaluation: skipped")

    print("=" * 60)


if __name__ == "__main__":
    main()
