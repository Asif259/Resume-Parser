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

