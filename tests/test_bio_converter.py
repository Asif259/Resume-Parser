import pytest
from pathlib import Path
from tools.annotation_schema import BIO_TAGS
from tools.bio_converter import convert_to_bio, save_bio_file, load_bio_file
from tests.evaluation.ground_truth import GroundTruth
from app.schemas.resume import ParsedResume, PersonalInfo, Experience

def test_bio_tags_defined():
    assert "PERSON_NAME" in BIO_TAGS
    assert "JOB_TITLE" in BIO_TAGS
    assert "COMPANY" in BIO_TAGS
    assert "SKILL" in BIO_TAGS

def test_convert_to_bio_simple():
    text = "John Doe john@email.com Software Engineer at Google"
    gt = GroundTruth(
        resume_id="test",
        source_file="test.pdf",
        expected=ParsedResume(
            personal_info=PersonalInfo(name="John Doe", email="john@email.com"),
            experience=[Experience(job_title="Software Engineer", company="Google")],
            skills=[],
            education=[],
            certifications=[],
            projects=[],
            languages=[],
            raw_text=text,
        ),
    )
    bio = convert_to_bio(text, gt)
    assert len(bio) > 0
    # Check tokens and tags
    tokens = [t[0] for t in bio]
    tags = [t[1] for t in bio]

    assert "John" in tokens
    john_idx = tokens.index("John")
    assert tags[john_idx] == "B-PERSON_NAME"
    assert tags[john_idx + 1] == "I-PERSON_NAME"

    assert "john@email.com" in tokens
    email_idx = tokens.index("john@email.com")
    assert tags[email_idx] == "B-EMAIL"

    assert "Google" in tokens
    google_idx = tokens.index("Google")
    assert tags[google_idx] == "B-COMPANY"

def test_bio_roundtrip(tmp_path: Path):
    bio_data = [
        ("John", "B-PERSON_NAME"),
        ("Doe", "I-PERSON_NAME"),
        ("works", "O"),
        ("at", "O"),
        ("Google", "B-COMPANY"),
    ]
    out_file = tmp_path / "dataset.bio"
    save_bio_file(bio_data, out_file)
    loaded = load_bio_file(out_file)
    assert loaded == bio_data

