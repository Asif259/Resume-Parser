from pathlib import Path
import pytest
from app.services.entity_extractor import ExtractedEntities
from app.schemas.evidence import FieldEvidence
from app.services.reconciliation import ReconciliationStrategy
from app.services.hybrid_extractor import HybridExtractor
from app.services.ab_compare import compute_deltas, format_ab_report
from tests.evaluation.runner import EvaluationReport
from tests.evaluation.metrics import EvaluationMetrics

def test_reconciliation_strategy_agreement():
    reconciler = ReconciliationStrategy()
    rules = ExtractedEntities(
        name="John Doe",
        email="john@example.com",
        location="San Francisco, USA",
        evidence={
            "personal_info.name": FieldEvidence(
                value="John Doe",
                source_section="header",
                source_text="John Doe",
                confidence=0.85,
                extraction_method="rules",
            )
        }
    )
    ml_entities = [
        {"entity": "John Doe", "label": "PERSON_NAME", "confidence": 0.92, "start": 0, "end": 8},
        {"entity": "Google", "label": "COMPANY", "confidence": 0.88, "start": 20, "end": 26},
    ]

    merged = reconciler.merge(rules, ml_entities)
    assert merged.name == "John Doe"
    assert "personal_info.name" in merged.evidence
    assert merged.evidence["personal_info.name"].extraction_method == "hybrid"
    assert merged.evidence["personal_info.name"].confidence >= 0.85
    assert "Google" in merged.companies

def test_reconciliation_unions_job_titles():
    reconciler = ReconciliationStrategy()
    rules = ExtractedEntities(
        job_titles=["Software Engineer"]
    )
    ml_entities = [
        {"entity": "Backend Developer", "label": "JOB_TITLE", "confidence": 0.82, "start": 0, "end": 17}
    ]

    merged = reconciler.merge(rules, ml_entities)
    assert "Software Engineer" in merged.job_titles
    assert "Backend Developer" in merged.job_titles

def test_hybrid_extractor_fallback():
    extractor = HybridExtractor(use_ml=False)
    sections = {"header": "Alice Smith alice@test.com"}
    entities = extractor.extract(sections, raw_text="")
    assert entities.email == "alice@test.com"

def test_compute_deltas():
    r_metrics = EvaluationMetrics(
        precision=0.9, recall=0.8, f1=0.85, exact_matches=10, total_fields=12,
        field_scores={"personal_info.name": 0.80, "skills": 0.85}
    )
    h_metrics = EvaluationMetrics(
        precision=0.92, recall=0.85, f1=0.88, exact_matches=11, total_fields=12,
        field_scores={"personal_info.name": 0.90, "skills": 0.90}
    )
    r_rep = EvaluationReport(overall=r_metrics, per_resume={}, per_field=r_metrics.field_scores)
    h_rep = EvaluationReport(overall=h_metrics, per_resume={}, per_field=h_metrics.field_scores)

    deltas = compute_deltas(r_rep, h_rep)
    assert deltas["personal_info.name"] == pytest.approx(0.10, abs=0.01)
    assert deltas["skills"] == pytest.approx(0.05, abs=0.01)

    table = format_ab_report({
        "rules": {"precision": 0.9, "recall": 0.8, "f1": 0.85, "exact_matches": 10, "total_fields": 12, "field_scores": {}},
        "hybrid": {"precision": 0.92, "recall": 0.85, "f1": 0.88, "exact_matches": 11, "total_fields": 12, "field_scores": {}},
        "deltas": {"precision": 0.02, "recall": 0.05, "f1": 0.03, "exact_matches": 1, "per_field": deltas},
    })
    assert "PIPELINE A/B COMPARISON REPORT" in table
