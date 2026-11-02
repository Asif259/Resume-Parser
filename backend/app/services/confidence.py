from typing import Dict, List
from app.schemas.evidence import FieldEvidence

FIELD_WEIGHTS = {
    "personal_info.name": 2.0,
    "personal_info.email": 2.0,
    "personal_info.phone": 1.5,
    "personal_info.location": 1.0,
    "professional_summary": 1.0,
}

def compute_overall_confidence(evidence: Dict[str, FieldEvidence]) -> float:
    """Computes a weighted confidence score for the entire parsed resume between 0.0 and 1.0."""
    if not evidence:
        return 0.5

    total_weight = 0.0
    weighted_sum = 0.0

    for key, ev in evidence.items():
        if key in FIELD_WEIGHTS:
            weight = FIELD_WEIGHTS[key]
        elif key.startswith("experience."):
            weight = 1.2
        elif key.startswith("education."):
            weight = 1.0
        elif key.startswith("skills."):
            weight = 0.5
        else:
            weight = 1.0

        conf = ev.calibrated_confidence if ev.calibrated_confidence is not None else ev.confidence
        conf = max(0.0, min(1.0, conf))
        weighted_sum += conf * weight
        total_weight += weight

    if total_weight == 0:
        return 0.5

    return round(weighted_sum / total_weight, 4)

def flag_low_confidence(evidence: Dict[str, FieldEvidence], threshold: float = 0.6) -> List[str]:
    """Returns a sorted list of field keys where extraction confidence is below the threshold."""
    low_fields: List[str] = []
    for key, ev in evidence.items():
        effective_conf = ev.calibrated_confidence if ev.calibrated_confidence is not None else ev.confidence
        if effective_conf < threshold:
            low_fields.append(key)
    return sorted(low_fields)

