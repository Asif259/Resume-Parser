from app.services.section_detector import detect_sections

def test_detects_experience_and_education():
    text = "EXPERIENCE\nSoftware Engineer at ABC\n2022-2024\n\nEDUCATION\nBSc Computer Science\nXYZ University"
    sections = detect_sections(text)
    assert "Software Engineer" in sections["experience"]
    assert "BSc Computer Science" in sections["education"]

def test_mixed_case_headings_and_colons():
    text = "Work Experience:\nDeveloper at X\n\nskills\nPython, Java"
    sections = detect_sections(text)
    assert "Developer" in sections["experience"]
    assert "Python" in sections["skills"]

def test_personal_info_before_first_heading():
    text = "John Smith\njohn@email.com\n+1 555 123 4567\n\nPROFESSIONAL SUMMARY\nExperienced developer."
    sections = detect_sections(text)
    assert "John Smith" in sections["personal_info"]
    assert "Experienced developer" in sections["summary"]

def test_no_headings_all_personal_info():
    text = "John Smith\njohn@email.com\nSome random text"
    sections = detect_sections(text)
    assert "John Smith" in sections["personal_info"]

def test_certifications_and_projects():
    text = "CERTIFICATIONS\nAWS Solutions Architect\n\nPROJECTS\nE-commerce platform"
    sections = detect_sections(text)
    assert "AWS" in sections["certifications"]
    assert "E-commerce" in sections["projects"]

def test_languages_section():
    text = "SKILLS\nPython, React\n\nLANGUAGES\nEnglish, Spanish"
    sections = detect_sections(text)
    assert "Python" in sections["skills"]
    assert "English" in sections["languages"]
