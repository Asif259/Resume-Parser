from tests.evaluation.runner import EvaluationReport

def format_report(report: EvaluationReport) -> str:
    lines = [
        "=" * 68,
        "                     EVALUATION REPORT",
        "=" * 68,
        f"{'Resume ID':<25} | {'Precision':<9} | {'Recall':<9} | {'F1':<9} | {'Exact'}",
        "-" * 68,
    ]
    for r_id, m in sorted(report.per_resume.items()):
        lines.append(
            f"{r_id:<25} | {m.precision:<9.4f} | {m.recall:<9.4f} | {m.f1:<9.4f} | {m.exact_matches}/{m.total_fields}"
        )

    lines.append("-" * 68)
    o = report.overall
    lines.append(
        f"{'OVERALL':<25} | {o.precision:<9.4f} | {o.recall:<9.4f} | {o.f1:<9.4f} | {o.exact_matches}/{o.total_fields}"
    )
    lines.append("=" * 68)
    lines.append("\nFIELD-LEVEL ACCURACY:")
    for field_name, score in sorted(report.per_field.items()):
        lines.append(f"  - {field_name:<30}: {score * 100:.1f}%")
    lines.append("=" * 68)

    return "\n".join(lines)
