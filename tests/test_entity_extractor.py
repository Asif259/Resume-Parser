import pytest
from app.services.entity_extractor import extract_entities, ExtractedEntities

def test_extract_email():
    entities = extract_entities({"personal_info": "Contact: john.smith@email.com"})
    assert entities.email == "john.smith@email.com"

def test_extract_phone():
    entities = extract_entities({"personal_info": "Phone: +1 555 123 4567"})
    assert "+1 555 123 4567" in entities.phone

def test_extract_name_via_spacy():
    entities = extract_entities({"personal_info": "John Smith\njohn@email.com\n+1 555 1234"})
    assert entities.name is not None
    assert "John" in entities.name

def test_extract_dates_from_experience():
    entities = extract_entities({"experience": "Software Engineer\nABC Corp\nJanuary 2023 - Present"})
    assert len(entities.dates) >= 1

def test_extract_location():
    entities = extract_entities({"personal_info": "John Smith\njohn@email.com\nNew York, USA"})
    assert entities.location is not None

def test_extract_linkedin_github():
    entities = extract_entities({
        "personal_info": "github.com/johnsmith\nlinkedin.com/in/johnsmith"
    })
    assert entities.github is not None
    assert entities.linkedin is not None

def test_unicode_email():
    entities = extract_entities({"personal_info": "rené.müller@example.com"})
    assert entities.email is not None

def test_company_name_not_extracted_as_person():
    sections = {"personal_info": "Google Technologies Inc\nJohn Smith\njohn@email.com"}
    result = extract_entities(sections)
    assert result.name == "John Smith"
    assert result.name != "Google Technologies Inc"

def test_section_heading_not_extracted_as_name():
    sections = {"personal_info": "Experience\nJane Doe\njane@email.com"}
    result = extract_entities(sections)
    assert result.name == "Jane Doe"

def test_resume_header_or_job_title_not_extracted_as_name():
    sections1 = {"personal_info": "Curriculum Vitae\nJane Doe\njane@email.com"}
    result1 = extract_entities(sections1)
    assert result1.name == "Jane Doe"

    sections2 = {"personal_info": "Senior Software Engineer\nJane Doe\njane@email.com"}
    result2 = extract_entities(sections2)
    assert result2.name == "Jane Doe"

def test_prefers_name_from_first_lines():
    sections = {
        "personal_info": "Alice Johnson\nalice@email.com\n555-1234",
        "experience": "Worked with Bob Smith at Acme Corp"
    }
    result = extract_entities(sections)
    assert result.name == "Alice Johnson"

