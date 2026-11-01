from app.services.information_grouper import group_information
from app.services.entity_extractor import extract_entities

def test_groups_experience_records():
    sections = {
        "experience": "Senior Developer\nABC Technologies\n2022 - Present\nBuilt microservices.\nManaged team of 5.\n\nJunior Developer\nXYZ Solutions\n2020 - 2022\nDeveloped REST APIs."
    }
    entities = extract_entities(sections)
    grouped = group_information(sections, entities)
    assert len(grouped.experience) >= 2
    assert grouped.experience[0]["job_title"] is not None
    assert grouped.experience[0]["company"] is not None

def test_groups_education_records():
    sections = {
        "education": "Bachelor of Computer Science\nXYZ University\n2022\n\nMaster of Data Science\nABC University\n2024"
    }
    entities = extract_entities(sections)
    grouped = group_information(sections, entities)
    assert len(grouped.education) >= 2

def test_single_experience_entry():
    sections = {
        "experience": "Software Engineer\nGoogle\nJanuary 2023 - Present\nDeveloped search features."
    }
    entities = extract_entities(sections)
    grouped = group_information(sections, entities)
    assert len(grouped.experience) >= 1
    exp = grouped.experience[0]
    assert exp["description"]

def test_empty_sections():
    sections = {}
    entities = extract_entities(sections)
    grouped = group_information(sections, entities)
    assert grouped.experience == []
    assert grouped.education == []

def test_compact_format_no_blank_lines():
    """Experience entries separated by date lines, no blank lines."""
    text = (
        "Software Engineer\nAcme Corp\nJan 2020 - Present\n"
        "- Built APIs\n- Led team\n"
        "Junior Developer\nStartup Inc\nJun 2018 - Dec 2019\n"
        "- Wrote tests"
    )
    sections = {"experience": text}
    entities = extract_entities(sections)
    result = group_information(sections, entities)
    assert len(result.experience) == 2
    assert result.experience[0]["job_title"] == "Software Engineer"
    assert result.experience[1]["job_title"] == "Junior Developer"

def test_company_first_format():
    text = "Google\nSoftware Engineer\nJan 2020 - Present\n- Built systems"
    sections = {"experience": text}
    result = group_information(sections, extract_entities(sections))
    assert result.experience[0]["company"] == "Google"
    assert result.experience[0]["job_title"] == "Software Engineer"

def test_pipe_separator_title_company():
    text = "Software Engineer | Acme Corp\nJan 2020 - Dec 2022\n- Did work"
    sections = {"experience": text}
    result = group_information(sections, extract_entities(sections))
    assert result.experience[0]["job_title"] == "Software Engineer"
    assert result.experience[0]["company"] == "Acme Corp"

