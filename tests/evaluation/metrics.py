from dataclasses import dataclass, field
from typing import Dict, List
from tests.evaluation.comparator import FieldComparison

@dataclass
class EvaluationMetrics:
    precision: float
    recall: float
    f1: float
    exact_matches: int
    total_fields: int
    field_scores: Dict[str, float] = field(default_factory=dict)

def compute_metrics(comparisons: List[FieldComparison]) -> EvaluationMetrics:
    if not comparisons:
        return EvaluationMetrics(
            precision=1.0,
            recall=1.0,
            f1=1.0,
            exact_matches=0,
            total_fields=0,
            field_scores={},
        )

    exact_matches = sum(1 for c in comparisons if c.match)
    total_fields = len(comparisons)
    
    # Calculate precision, recall, f1 based on similarity scores
    # Recall = sum of similarity / total expected evaluated fields
    recall = sum(c.similarity for c in comparisons) / total_fields
    
    # Precision: penalty for non-matches where actual was populated incorrectly vs correctly
    matched_score = sum(c.similarity for c in comparisons)
    actual_present = sum(1 for c in comparisons if c.actual is not None)
    if actual_present > 0:
        precision = matched_score / actual_present
        # Cap precision at 1.0
        precision = min(1.0, precision)
    else:
        precision = 1.0 if total_fields == 0 else 0.0

    if precision + recall > 0:
        f1 = (2 * precision * recall) / (precision + recall)
    else:
        f1 = 0.0

    # Field-level average scores
    field_scores: Dict[str, float] = {}
    field_counts: Dict[str, int] = {}
    for c in comparisons:
        base_field = c.field.split(".")[0]
        if base_field in ("personal_info", "experience", "education"):
            # keep subfield name, e.g. "personal_info.email" or "experience.job_title"
            parts = c.field.split(".")
            if len(parts) >= 3 and parts[1].isdigit():
                # e.g. experience.0.job_title -> experience.job_title
                key = f"{parts[0]}.{parts[2]}"
            else:
                key = c.field
        else:
            key = c.field

        field_scores[key] = field_scores.get(key, 0.0) + c.similarity
        field_counts[key] = field_counts.get(key, 0) + 1

    for k in field_scores:
        field_scores[k] = round(field_scores[k] / field_counts[k], 4)

    return EvaluationMetrics(
        precision=round(precision, 4),
        recall=round(recall, 4),
        f1=round(f1, 4),
        exact_matches=exact_matches,
        total_fields=total_fields,
        field_scores=field_scores,
    )
