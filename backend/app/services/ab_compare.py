from pathlib import Path
from typing import Any, Union
from tests.evaluation.runner import run_evaluation, EvaluationReport

def compute_deltas(rules_report: EvaluationReport, hybrid_report: EvaluationReport) -> dict[str, float]:
    """Computes field-level accuracy differences (hybrid - rules)."""
    deltas: dict[str, float] = {}
    all_fields = set(rules_report.per_field.keys()) | set(hybrid_report.per_field.keys())

    for field in sorted(all_fields):
        r_score = rules_report.per_field.get(field, 0.0)
        h_score = hybrid_report.per_field.get(field, 0.0)
        deltas[field] = round(h_score - r_score, 4)

    return deltas

def compare_pipelines(
    fixtures_dir: Union[str, Path],
    ground_truth_dir: Union[str, Path],
) -> dict[str, Any]:
    """Runs A/B evaluation between Rule-based and Hybrid (ML + Semantic) pipelines."""
    fixtures_dir = Path(fixtures_dir)
    ground_truth_dir = Path(ground_truth_dir)

    rules_report = run_evaluation(
        fixtures_dir=fixtures_dir,
        ground_truth_dir=ground_truth_dir,
        use_ml=False,
        use_semantic=False,
    )

    hybrid_report = run_evaluation(
        fixtures_dir=fixtures_dir,
        ground_truth_dir=ground_truth_dir,
        use_ml=True,
        use_semantic=True,
    )

    field_deltas = compute_deltas(rules_report, hybrid_report)

    return {
        "rules": {
            "precision": rules_report.overall.precision,
            "recall": rules_report.overall.recall,
            "f1": rules_report.overall.f1,
            "exact_matches": rules_report.overall.exact_matches,
            "total_fields": rules_report.overall.total_fields,
            "field_scores": rules_report.per_field,
        },
        "hybrid": {
            "precision": hybrid_report.overall.precision,
            "recall": hybrid_report.overall.recall,
            "f1": hybrid_report.overall.f1,
            "exact_matches": hybrid_report.overall.exact_matches,
            "total_fields": hybrid_report.overall.total_fields,
            "field_scores": hybrid_report.per_field,
        },
        "deltas": {
            "precision": round(hybrid_report.overall.precision - rules_report.overall.precision, 4),
            "recall": round(hybrid_report.overall.recall - rules_report.overall.recall, 4),
            "f1": round(hybrid_report.overall.f1 - rules_report.overall.f1, 4),
            "exact_matches": hybrid_report.overall.exact_matches - rules_report.overall.exact_matches,
            "per_field": field_deltas,
        },
    }

def format_ab_report(comparison: dict[str, Any]) -> str:
    """Formats comparison results as a clean text table."""
    r = comparison["rules"]
    h = comparison["hybrid"]
    d = comparison["deltas"]

    lines = [
        "=" * 60,
        "         PIPELINE A/B COMPARISON REPORT",
        "=" * 60,
        f"{'Metric':<20} | {'Rules':<12} | {'Hybrid':<12} | {'Delta':<10}",
        "-" * 60,
        f"{'Precision':<20} | {r['precision']*100:>10.2f}% | {h['precision']*100:>10.2f}% | {d['precision']*100:>+8.2f}%",
        f"{'Recall':<20} | {r['recall']*100:>10.2f}% | {h['recall']*100:>10.2f}% | {d['recall']*100:>+8.2f}%",
        f"{'F1-Score':<20} | {r['f1']*100:>10.2f}% | {h['f1']*100:>10.2f}% | {d['f1']*100:>+8.2f}%",
        f"{'Exact Matches':<20} | {r['exact_matches']:>11} | {h['exact_matches']:>11} | {d['exact_matches']:>+9}",
        "-" * 60,
        "Field-Level Accuracy Deltas:",
    ]

    for f_name, delta in d["per_field"].items():
        symbol = "=" if delta == 0 else ("+" if delta > 0 else "")
        lines.append(f"  {f_name:<30}: {symbol}{delta*100:.2f}%")

    lines.append("=" * 60)
    return "\n".join(lines)

