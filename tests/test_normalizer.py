import pytest
from app.services.normalizer import normalize_date, normalize_phone, normalize
from app.services.information_grouper import GroupedInfo
from app.services.entity_extractor import ExtractedEntities
from app.schemas.resume import ParsedResume

def test_normalize_date_formats():
    assert normalize_date("Jan 2023") == "2023-01"
    assert normalize_date("January 2023") == "2023-01"
    assert normalize_date("Oct. 2022") == "2022-10"
    assert normalize_date("2023") == "2023"
    assert normalize_date("Present") is None
    assert normalize_date("Current") is None
    assert normalize_date(None) is None
    assert normalize_date("invalid-date") == "invalid-date"

def test_normalize_phone():
    assert normalize_phone("+1  555  123 4567") == "+1 555 123 4567"
    assert normalize_phone(None) is None

def test_normalize_assembles_parsed_resume():
    sections = {
        "personal_info": "John Smith\njohn.smith@email.com\n+1 555 123 4567\nNew York, USA",
        "summary": "Full-stack developer with 3 years of experience.",
        "certifications": "AWS Certified Solutions Architect (Amazon, 2023)",
        "projects": "Portfolio Website: Built with React and Next.js.",
        "languages": "English (Native), Spanish (Intermediate)"
    }
    entities = ExtractedEntities(
        name="John Smith",
        email="john.smith@email.com",
        phone="+1 555 123 4567",
        location="New York, USA",
        linkedin="https://linkedin.com/in/johnsmith",
        github="https://github.com/johnsmith"
    )
    grouped = GroupedInfo(
        experience=[
            {
                "job_title": "Software Engineer",
                "company": "ABC Technologies",
                "start_date": "January 2023",
                "end_date": "Present",
                "description": ["Developed web apps"]
            }
        ],
        education=[
            {
                "degree": "Bachelor of Computer Science",
                "institution": "XYZ University",
                "graduation_year": 2022
            }
        ]
    )
    skills = ["JavaScript", "TypeScript", "React", "Node.js"]

    resume = normalize(
        sections=sections,
        entities=entities,
        grouped=grouped,
        skills=skills,
        raw_text="raw resume text"
    )

    assert isinstance(resume, ParsedResume)
    assert resume.personal_info.name == "John Smith"
    assert resume.personal_info.email == "john.smith@email.com"
    assert resume.personal_info.linkedin == "https://linkedin.com/in/johnsmith"
    assert resume.professional_summary == "Full-stack developer with 3 years of experience."
    assert resume.skills == ["JavaScript", "TypeScript", "React", "Node.js"]
    assert len(resume.experience) == 1
    assert resume.experience[0].start_date == "2023-01"
    assert resume.experience[0].end_date is None
    assert resume.education[0].graduation_year == 2022
    assert len(resume.certifications) >= 1
    assert len(resume.projects) >= 1
    assert "English" in resume.languages[0]

