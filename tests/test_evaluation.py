import json
from pathlib import Path
import pytest
from app.schemas.resume import ParsedResume, PersonalInfo, Experience, Education
from tests.evaluation.ground_truth import GroundTruth, load_ground_truth, load_ground_truth_dir
from tests.evaluation.comparator import compare_resumes, FieldComparison
from tests.evaluation.metrics import compute_metrics, EvaluationMetrics
from tests.evaluation.runner import run_evaluation, EvaluationReport
from tests.evaluation.report import format_report

def test_ground_truth_loads_valid_json(tmp_path: Path):
    gt_file = tmp_path / "sample.json"
    gt_file.write_text(json.dumps({
        "resume_id": "test-1",
        "source_file": "test.pdf",
        "expected": {
            "personal_info": {"name": "John Doe", "email": "john@example.com"},
            "skills": ["Python"],
            "experience": [],
            "education": [],
            "certifications": [],
            "projects": [],
            "languages": [],
            "raw_text": "..."
        }
    }))
    gt = load_ground_truth(gt_file)
    assert gt.resume_id == "test-1"
    assert gt.source_file == "test.pdf"
    assert gt.expected.personal_info.name == "John Doe"

def test_load_ground_truth_dir(tmp_path: Path):
    (tmp_path / "1.json").write_text(json.dumps({
        "resume_id": "r1",
        "source_file": "r1.pdf",
        "expected": {"skills": ["Python"]}
    }))
    (tmp_path / "2.json").write_text(json.dumps({
        "resume_id": "r2",
        "source_file": "r2.pdf",
        "expected": {"skills": ["Go"]}
    }))
    items = load_ground_truth_dir(tmp_path)
    assert len(items) == 2
    assert {it.resume_id for it in items} == {"r1", "r2"}

def test_compare_exact_match():
    expected = ParsedResume(
        personal_info=PersonalInfo(name="John Doe", email="john@example.com"),
        skills=["Python"],
    )
    actual = ParsedResume(
        personal_info=PersonalInfo(name="John Doe", email="john@example.com"),
        skills=["Python"],
    )
    comparisons = compare_resumes(expected, actual)
    name_cmp = next(c for c in comparisons if c.field == "personal_info.name")
    assert name_cmp.match is True
    assert name_cmp.similarity == 1.0

def test_compare_partial_skills():
    expected = ParsedResume(skills=["Python", "Java", "SQL"])
    actual = ParsedResume(skills=["Python", "Java"])
    comparisons = compare_resumes(expected, actual)
    skills_cmp = next(c for c in comparisons if c.field == "skills")
    # 2 out of 3 matched -> similarity ~0.667
    assert skills_cmp.similarity == pytest.approx(2 / 3, abs=0.01)

def test_compare_nested_experience():
    expected = ParsedResume(
        experience=[
            Experience(job_title="Software Engineer", company="Acme", start_date="2020-01", is_current=True)
        ]
    )
    actual = ParsedResume(
        experience=[
            Experience(job_title="Software Engineer", company="Acme", start_date="2020-01", is_current=True)
        ]
    )
    comparisons = compare_resumes(expected, actual)
    title_cmp = next(c for c in comparisons if c.field == "experience.0.job_title")
    assert title_cmp.match is True
    assert title_cmp.similarity == 1.0

def test_compute_metrics_perfect():
    comparisons = [
        FieldComparison(field="name", expected="A", actual="A", match=True, similarity=1.0),
        FieldComparison(field="email", expected="a@b.c", actual="a@b.c", match=True, similarity=1.0)
    ]
    metrics = compute_metrics(comparisons)
    assert metrics.f1 == 1.0
    assert metrics.precision == 1.0
    assert metrics.recall == 1.0
    assert metrics.exact_matches == 2
    assert metrics.total_fields == 2

def test_compute_metrics_partial():
    comparisons = [
        FieldComparison(field="name", expected="John", actual="John", match=True, similarity=1.0),
        FieldComparison(field="phone", expected="123", actual=None, match=False, similarity=0.0)
    ]
    metrics = compute_metrics(comparisons)
    assert 0.0 < metrics.f1 < 1.0
    assert metrics.exact_matches == 1
    assert metrics.total_fields == 2

def test_evaluation_runner_produces_report():
    fixtures_dir = Path(__file__).resolve().parent / "fixtures" / "resumes"
    gt_dir = Path(__file__).resolve().parent / "fixtures" / "ground_truth"
    report = run_evaluation(fixtures_dir=fixtures_dir, ground_truth_dir=gt_dir)
    assert isinstance(report, EvaluationReport)
    assert len(report.per_resume) == 5
    assert 0.0 <= report.overall.f1 <= 1.0
    formatted = format_report(report)
    assert "EVALUATION REPORT" in formatted

def test_baseline_email_accuracy():
    fixtures_dir = Path(__file__).resolve().parent / "fixtures" / "resumes"
    gt_dir = Path(__file__).resolve().parent / "fixtures" / "ground_truth"
    report = run_evaluation(fixtures_dir=fixtures_dir, ground_truth_dir=gt_dir)
    assert report.per_field.get("personal_info.email", 0.0) >= 0.8
