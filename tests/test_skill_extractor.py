from app.services.skill_extractor import extract_skills

def test_extracts_listed_skills():
    sections = {"skills": "JavaScript, TypeScript, React, Node.js, PostgreSQL"}
    skills = extract_skills(sections)
    assert "JavaScript" in skills
    assert "TypeScript" in skills
    assert "React" in skills
    assert "Node.js" in skills
    assert "PostgreSQL" in skills

def test_normalizes_skill_variants():
    sections = {"skills": "ReactJS, node js, postgres, golang"}
    skills = extract_skills(sections)
    assert "React" in skills
    assert "Node.js" in skills
    assert "PostgreSQL" in skills
    assert "Go" in skills

def test_no_false_positive_go_in_google():
    sections = {"experience": "Worked at Google on search infrastructure"}
    skills = extract_skills(sections)
    assert "Go" not in skills

def test_deduplicates():
    sections = {"skills": "React, ReactJS, React.js"}
    skills = extract_skills(sections)
    assert skills.count("React") == 1

def test_extracts_from_experience_section():
    sections = {
        "skills": "Python",
        "experience": "Built applications using Django and PostgreSQL"
    }
    skills = extract_skills(sections)
    assert "Python" in skills
    assert "Django" in skills
    assert "PostgreSQL" in skills

def test_case_insensitive_matching():
    sections = {"skills": "python, JAVASCRIPT, Docker"}
    skills = extract_skills(sections)
    assert "Python" in skills
    assert "JavaScript" in skills
    assert "Docker" in skills
