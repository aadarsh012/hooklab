"""Generate the comprehensive Phase 5 evaluation report."""

from typing import Dict


def generate_eval_report(
    prediction_data: Dict,
    pva_data: Dict,
    rewrite_data: Dict,
    rewrite_scores: Dict,
    generated_at: str,
    output_path: str = "eval/REPORT.md",
) -> str:
    """Write the full evaluation report as Markdown.

    Returns the report content as a string.
    """
    lines = []
    lines.append("# HookLab — Evaluation Report\n")
    lines.append(f"Generated: {generated_at}\n")

    # --- Dataset ---
    lines.append("## Dataset\n")
    lines.append(f"- Test set: {prediction_data['total']} hooks")
    strong_count = pva_data["strong_stats"]["count"]
    weak_count = pva_data["weak_stats"]["count"]
    lines.append(f"- Distribution: {strong_count} strong, {weak_count} weak")
    lines.append("- Features: 384-dim sentence-transformer embeddings (all-MiniLM-L6-v2)\n")

    # --- ML Classifier Performance ---
    lines.append("## ML Classifier Performance\n")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Accuracy | {prediction_data['accuracy']:.2%} |")
    lines.append(f"| Precision | {prediction_data['precision']:.2%} |")
    lines.append(f"| Recall | {prediction_data['recall']:.2%} |")
    lines.append(f"| F1 Score | {prediction_data['f1']:.2%} |")
    lines.append(f"| Correct | {prediction_data['correct']}/{prediction_data['total']} |")
    lines.append("")

    # Confusion matrix
    cm = prediction_data["confusion_matrix"]
    if len(cm) == 2:
        lines.append("### Confusion Matrix\n")
        lines.append("```")
        lines.append("              Predicted")
        lines.append("              weak  strong")
        lines.append(f"Actual weak   {cm[0][0]:4d}  {cm[0][1]:4d}")
        lines.append(f"Actual strong {cm[1][0]:4d}  {cm[1][1]:4d}")
        lines.append("```\n")

    # --- Predicted vs Actual ---
    lines.append("## Predicted vs Actual\n")
    lines.append("### Per-Label Breakdown\n")
    lines.append("| True Label | Count | Accuracy | Mean Confidence |")
    lines.append("|------------|-------|----------|-----------------|")
    for label_name, stats in [("strong", pva_data["strong_stats"]), ("weak", pva_data["weak_stats"])]:
        lines.append(
            f"| {label_name} | {stats['count']} | {stats['accuracy']:.2%} | "
            f"{stats['mean_confidence']:.2%} |"
        )
    lines.append("")

    # Overconfident wrong
    overconfident = pva_data["overconfident_wrong"]
    if overconfident:
        lines.append("### Overconfident Wrong Predictions (confidence >80% but incorrect)\n")
        lines.append("| Hook Text | True | Predicted | Confidence |")
        lines.append("|-----------|------|-----------|------------|")
        for h in overconfident:
            hook_short = h["hook_text"][:60] + "..." if len(h["hook_text"]) > 60 else h["hook_text"]
            lines.append(f"| {hook_short} | {h['true_label']} | {h['predicted_label']} | {h['confidence']:.2%} |")
        lines.append("")
    else:
        lines.append("### Overconfident Wrong Predictions\n")
        lines.append("None found — no predictions were both wrong and >80% confident.\n")

    # Underconfident correct
    underconfident = pva_data["underconfident_correct"]
    if underconfident:
        lines.append("### Underconfident Correct Predictions (confidence <60% but correct)\n")
        lines.append("| Hook Text | True | Predicted | Confidence |")
        lines.append("|-----------|------|-----------|------------|")
        for h in underconfident:
            hook_short = h["hook_text"][:60] + "..." if len(h["hook_text"]) > 60 else h["hook_text"]
            lines.append(f"| {hook_short} | {h['true_label']} | {h['predicted_label']} | {h['confidence']:.2%} |")
        lines.append("")
    else:
        lines.append("### Underconfident Correct Predictions\n")
        lines.append("None found.\n")

    # --- Rewriter Evaluation ---
    if rewrite_data.get("total_judgments", 0) > 0:
        lines.append("## Rewriter Evaluation\n")
        lines.append("> **Disclosure:** LLM-as-judge was used for blind comparison. "
                     "This is not a substitute for human evaluation.\n")
        lines.append(f"- Hooks evaluated: {len(set(j['original'] for j in rewrite_data['judgments']))}")
        lines.append(f"- Total rewrite comparisons: {rewrite_data['total_judgments']}")
        lines.append(f"- Judge prefers rewrite: **{rewrite_data['preference_rate']:.0%}** "
                     f"({rewrite_data['rewrite_wins']}/{rewrite_data['total_judgments']})")

        if rewrite_scores.get("total", 0) > 0:
            lines.append(f"- Classifier upgrade rate: **{rewrite_scores['upgrade_rate']:.0%}** "
                         f"({rewrite_scores['upgrades']}/{rewrite_scores['total']} "
                         f"rewrites classified as strong)")
        lines.append("")

        # Per-hook comparison table
        lines.append("### Rewrite Comparisons\n")
        lines.append("| Original | Rewrite | Judge Prefers | Classifier Upgrade |")
        lines.append("|----------|---------|---------------|-------------------|")
        scored = rewrite_scores.get("scored", [])
        for s in scored:
            orig_short = s["original"][:40] + "..." if len(s["original"]) > 40 else s["original"]
            rw_short = s["rewrite"][:40] + "..." if len(s["rewrite"]) > 40 else s["rewrite"]
            upgrade_str = "Yes" if s["is_upgrade"] else "No"
            lines.append(f"| {orig_short} | {rw_short} | {s['judge_prefers']} | {upgrade_str} |")
        lines.append("")
    else:
        lines.append("## Rewriter Evaluation\n")
        lines.append("Rewriter evaluation was skipped.\n")

    # --- Failure Analysis ---
    lines.append("## Failure Analysis\n")
    wrong = [r for r in prediction_data["per_hook_results"] if not r["correct"]]
    if wrong:
        lines.append(f"{len(wrong)} out of {prediction_data['total']} hooks were misclassified.\n")

        # High confidence failures are most concerning
        high_conf_wrong = [r for r in wrong if r["confidence"] > 0.7]
        if high_conf_wrong:
            lines.append("### High-Confidence Failures (confidence >70%)\n")
            lines.append("These are the most concerning — the model is confident but wrong:\n")
            for r in high_conf_wrong:
                hook_short = r["hook_text"][:70] + "..." if len(r["hook_text"]) > 70 else r["hook_text"]
                lines.append(f"- \"{hook_short}\" — true: {r['true_label']}, "
                             f"predicted: {r['predicted_label']} ({r['confidence']:.0%})")
            lines.append("")

        # Low confidence failures are borderline
        low_conf_wrong = [r for r in wrong if r["confidence"] <= 0.7]
        if low_conf_wrong:
            lines.append(f"### Borderline Failures ({len(low_conf_wrong)} hooks with confidence <=70%)\n")
            lines.append("These are understandable — the model was unsure:\n")
            for r in low_conf_wrong:
                hook_short = r["hook_text"][:70] + "..." if len(r["hook_text"]) > 70 else r["hook_text"]
                lines.append(f"- \"{hook_short}\" — true: {r['true_label']}, "
                             f"predicted: {r['predicted_label']} ({r['confidence']:.0%})")
            lines.append("")
    else:
        lines.append("No misclassifications on the test set.\n")

    # --- Honest Limitations ---
    lines.append("## Honest Limitations\n")
    lines.append("- **Small dataset:** 213 total hooks is far below the 400 target. "
                 "Results are directional, not statistically significant.")
    lines.append("- **Classifier underperforms baseline:** The ML model does not beat "
                 "the simple hook_length baseline. This suggests embeddings alone may not "
                 "capture what makes a hook strong — or the dataset is too small for the "
                 "model to learn meaningful patterns.")
    lines.append("- **LLM-as-judge is not ground truth:** The rewriter evaluation uses "
                 "an LLM to judge quality. This is disclosed and should be validated with "
                 "human evaluation in future work.")
    lines.append("- **Dimension scores are LLM-generated:** The 4 dimension scores "
                 "(specificity, curiosity gap, clarity of payoff, concreteness) come from "
                 "an LLM, not from human annotators. There is no ground truth for these.")
    lines.append("- **Single niche:** All data is from fitness. Generalization to other "
                 "content verticals is unknown.")
    lines.append("- **What would help:** 500+ hooks with human-annotated dimension scores, "
                 "A/B test data from real content performance, and multi-niche expansion.\n")

    content = "\n".join(lines)

    with open(output_path, "w") as f:
        f.write(content)

    return content
