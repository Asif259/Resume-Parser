import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas.resume import (
    PersonalInfo,
    Experience,
    Education,
    Certification,
    Project,
    ParsedResume,
    ParseResponse,
)

def test_parsed_resume_valid():
    data = {
        "personal_info": {
            "name": "John Smith",
            "email": "john@email.com",
            "phone": "+1 555 123 4567",
            "location": "New York, USA",
        },
        "professional_summary": "Full-stack developer.",
        "skills": ["React", "Node.js"],
        "experience": [
            {
                "job_title": "Software Engineer",
                "company": "ABC Technologies",
                "start_date": "2023-01",
                "end_date": None,
                "description": ["Built REST APIs", "Managed databases"],
            }
        ],
        "education": [
            {
                "degree": "BSc Computer Science",
                "institution": "XYZ University",
                "graduation_year": 2022,
            }
        ],
        "certifications": [
            {
                "name": "AWS Certified Solutions Architect",
                "issuer": "Amazon Web Services",
                "date": "2023",
            }
        ],
        "projects": [
            {
                "name": "E-Commerce Platform",
                "description": "Built using React and Node.",
                "technologies": ["React", "Node.js"],
            }
        ],
        "languages": ["English", "Spanish"],
    }

    resume = ParsedResume(**data)
    assert resume.personal_info.name == "John Smith"
    assert resume.personal_info.email == "john@email.com"
    assert len(resume.experience) == 1
    assert resume.experience[0].end_date is None
    assert resume.education[0].graduation_year == 2022
    assert "React" in resume.skills

def test_invalid_email_rejected():
    with pytest.raises(ValidationError):
        PersonalInfo(name="John", email="not-an-email", phone=None, location=None)

def test_parse_response_model():
    resume = ParsedResume(
        personal_info=PersonalInfo(name="Alice"),
        skills=["Python"],
    )
    res = ParseResponse(
        id="test-uuid",
        filename="alice_resume.pdf",
        parsed_resume=resume,
        created_at=datetime.now(),
    )
    assert res.id == "test-uuid"
    assert res.parsed_resume.personal_info.name == "Alice"

def test_experience_is_current_field():
    exp = Experience(job_title="Engineer", is_current=True)
    assert exp.is_current is True

def test_experience_is_current_default_none():
    exp = Experience(job_title="Engineer")
    assert exp.is_current is None

