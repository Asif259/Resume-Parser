from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Union
from app.services.pipeline import parse_resume
from tests.evaluation.ground_truth import load_ground_truth_dir
from tests.evaluation.comparator import compare_resumes, FieldComparison
from tests.evaluation.metrics import compute_metrics, EvaluationMetrics

@dataclass
class EvaluationReport:
    overall: EvaluationMetrics
    per_resume: Dict[str, EvaluationMetrics]
    per_field: Dict[str, float]
    all_comparisons: List[FieldComparison] = field(default_factory=list)

def run_evaluation(
    fixtures_dir: Union[str, Path],
    ground_truth_dir: Union[str, Path]
) -> EvaluationReport:
    fixtures_dir = Path(fixtures_dir)
    ground_truth_dir = Path(ground_truth_dir)

    ground_truths = load_ground_truth_dir(ground_truth_dir)
    per_resume: Dict[str, EvaluationMetrics] = {}
    all_comparisons: List[FieldComparison] = []

    for gt in ground_truths:
        resume_path = fixtures_dir / gt.source_file
        if not resume_path.exists():
            # If resume file doesn't exist, skip or raise
            continue

        ext = resume_path.suffix.lstrip(".").lower()
        actual = parse_resume(resume_path, ext)
        comparisons = compare_resumes(gt.expected, actual)
        metrics = compute_metrics(comparisons)

        per_resume[gt.resume_id] = metrics
        all_comparisons.extend(comparisons)

    overall = compute_metrics(all_comparisons)
    per_field = overall.field_scores

    return EvaluationReport(
        overall=overall,
        per_resume=per_resume,
        per_field=per_field,
        all_comparisons=all_comparisons,
    )
