"""Generate a Markdown evaluation report from scoring results."""

from scoring.schemas import EvalReport


def generate_report(report: EvalReport, output_path: str = "eval/REPORT.md") -> str:
    """Write an evaluation report as Markdown.

    Returns the report content as a string.
    """
    lines = []
    lines.append("# HookLab Phase 3 — Scoring Model Evaluation\n")
    lines.append(f"Generated: {report.generated_at}\n")

    # Dataset summary
    if report.dataset_summary:
        lines.append("## Dataset\n")
        lines.append(report.dataset_summary + "\n")

    # Baselines table
    lines.append("## Baselines\n")
    lines.append("| Baseline | Accuracy | Precision | Recall |")
    lines.append("|----------|----------|-----------|--------|")
    for b in report.baselines:
        lines.append(f"| {b.name} | {b.accuracy:.2%} | {b.precision:.2%} | {b.recall:.2%} |")
    lines.append("")

    # Models table with baseline comparison
    best_baseline_acc = max(b.accuracy for b in report.baselines) if report.baselines else 0
    lines.append("## Models\n")
    lines.append("| Model | Accuracy | Precision | Recall | vs. Best Baseline |")
    lines.append("|-------|----------|-----------|--------|-------------------|")
    for m in report.models:
        diff = m.accuracy - best_baseline_acc
        sign = "+" if diff >= 0 else ""
        lines.append(
            f"| {m.model_name} | {m.accuracy:.2%} | {m.precision:.2%} | "
            f"{m.recall:.2%} | {sign}{diff:.2%} |"
        )
    lines.append("")

    # Confusion matrices
    lines.append("## Confusion Matrices\n")
    for m in report.models:
        lines.append(f"### {m.model_name}\n")
        lines.append("```")
        lines.append("              Predicted")
        lines.append("              weak  strong")
        if len(m.confusion_matrix) == 2 and all(len(row) == 2 for row in m.confusion_matrix):
            lines.append(f"Actual weak   {m.confusion_matrix[0][0]:4d}  {m.confusion_matrix[0][1]:4d}")
            lines.append(f"Actual strong {m.confusion_matrix[1][0]:4d}  {m.confusion_matrix[1][1]:4d}")
        lines.append("```\n")

    # Per-hook predictions
    lines.append("## Test Set Predictions\n")
    for m in report.models:
        lines.append(f"### {m.model_name}\n")
        lines.append("| Hook Text | True | Predicted | Confidence |")
        lines.append("|-----------|------|-----------|------------|")
        for p in m.test_predictions:
            hook_short = p.hook_text[:60] + "..." if len(p.hook_text) > 60 else p.hook_text
            match = "ok" if p.true_label == p.predicted_label else "WRONG"
            lines.append(
                f"| {hook_short} | {p.true_label} | {p.predicted_label} ({match}) | "
                f"{p.confidence:.2%} |"
            )
        lines.append("")

    # Failure analysis
    if report.failure_analysis:
        lines.append("## Failure Analysis\n")
        lines.append("| Hook Text | True | Predicted | Confidence | Notes |")
        lines.append("|-----------|------|-----------|------------|-------|")
        for f in report.failure_analysis:
            hook_short = f.hook_text[:60] + "..." if len(f.hook_text) > 60 else f.hook_text
            lines.append(
                f"| {hook_short} | {f.true_label} | {f.predicted_label} | "
                f"{f.confidence:.2%} | {f.notes} |"
            )
        lines.append("")
    else:
        lines.append("## Failure Analysis\n")
        lines.append("No misclassifications on the test set.\n")

    # Honest assessment
    lines.append("## Honest Assessment\n")
    any_beats = any(m.accuracy > best_baseline_acc for m in report.models)
    lines.append("- With a very small dataset, these numbers are not statistically meaningful.")
    lines.append("- Individual predictions swing accuracy by large percentages.")
    if any_beats:
        lines.append("- At least one model beats the best baseline, but this may not generalize.")
    else:
        lines.append("- No model beats the best baseline. This is reported honestly.")
    lines.append("- The methodology and infrastructure are the real deliverable at this scale.")
    lines.append("- More data (200+ hooks) is needed before drawing conclusions.\n")

    content = "\n".join(lines)

    with open(output_path, "w") as f:
        f.write(content)

    return content
