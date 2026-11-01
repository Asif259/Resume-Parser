import json
from pathlib import Path
import fitz  # PyMuPDF
from docx import Document

FIXTURES_DIR = Path(__file__).resolve().parent
RESUMES_DIR = FIXTURES_DIR / "resumes"
GROUND_TRUTH_DIR = FIXTURES_DIR / "ground_truth"

def generate_fixtures():
    RESUMES_DIR.mkdir(parents=True, exist_ok=True)
    GROUND_TRUTH_DIR.mkdir(parents=True, exist_ok=True)

    # 1. simple_single_column.pdf
    doc1 = fitz.open()
    page1 = doc1.new_page()
    text1 = (
        "Alice Johnson\n"
        "alice.johnson@example.com | +1 555 234 5678 | San Francisco, USA\n"
        "https://linkedin.com/in/alicejohnson | https://github.com/alicej\n\n"
        "Professional Summary\n"
        "Experienced Backend Developer specializing in Python, FastAPI, and PostgreSQL with 5 years in cloud systems.\n\n"
        "Work Experience\n"
        "Senior Backend Engineer, CloudCorp\n"
        "January 2021 - Present\n"
        "- Architected distributed microservices in Python and FastAPI\n"
        "- Optimized PostgreSQL database queries cutting latency by 40%\n\n"
        "Software Engineer, TechSolutions\n"
        "June 2018 - December 2020\n"
        "- Developed RESTful APIs using Python and Django\n"
        "- Maintained CI/CD pipelines with Docker\n\n"
        "Education\n"
        "Master of Science in Computer Science, Stanford University, 2018\n\n"
        "Skills\n"
        "Python, FastAPI, Django, PostgreSQL, Docker, Git, Linux\n\n"
        "Certifications\n"
        "AWS Certified Solutions Architect (Amazon, 2022)\n\n"
        "Languages\n"
        "English, French"
    )
    page1.insert_text((50, 60), text1, fontsize=10)
    pdf1_path = RESUMES_DIR / "simple_single_column.pdf"
    doc1.save(str(pdf1_path))
    doc1.close()

    gt1 = {
        "resume_id": "simple_single_column",
        "source_file": "simple_single_column.pdf",
        "expected": {
            "personal_info": {
                "name": "Alice Johnson",
                "email": "alice.johnson@example.com",
                "phone": "+1 555 234 5678",
                "location": "San Francisco, USA",
                "linkedin": "https://linkedin.com/in/alicejohnson",
                "github": "https://github.com/alicej"
            },
            "professional_summary": "Experienced Backend Developer specializing in Python, FastAPI, and PostgreSQL with 5 years in cloud systems.",
            "skills": ["Python", "FastAPI", "Django", "PostgreSQL", "Docker", "Git", "Linux"],
            "experience": [
                {
                    "job_title": "Senior Backend Engineer",
                    "company": "CloudCorp",
                    "start_date": "2021-01",
                    "end_date": None,
                    "is_current": True,
                    "description": [
                        "Architected distributed microservices in Python and FastAPI",
                        "Optimized PostgreSQL database queries cutting latency by 40%"
                    ]
                },
                {
                    "job_title": "Software Engineer",
                    "company": "TechSolutions",
                    "start_date": "2018-06",
                    "end_date": "2020-12",
                    "is_current": None,
                    "description": [
                        "Developed RESTful APIs using Python and Django",
                        "Maintained CI/CD pipelines with Docker"
                    ]
                }
            ],
            "education": [
                {
                    "degree": "Master of Science in Computer Science",
                    "institution": "Stanford University",
                    "graduation_year": 2018
                }
            ],
            "certifications": [
                {
                    "name": "AWS Certified Solutions Architect",
                    "issuer": "Amazon",
                    "date": "2022"
                }
            ],
            "languages": ["English", "French"],
            "raw_text": text1
        }
    }
    with open(GROUND_TRUTH_DIR / "simple_single_column.json", "w", encoding="utf-8") as f:
        json.dump(gt1, f, indent=2)

    # 2. compact_no_blanks.pdf (Experience with no blank lines between entries)
    doc2 = fitz.open()
    page2 = doc2.new_page()
    text2 = (
        "Bob Williams\n"
        "bob.williams@email.com | +1 555 345 6789 | Chicago, USA\n"
        "Professional Summary\n"
        "Frontend Engineer focused on modern React and TypeScript.\n"
        "Work Experience\n"
        "Lead Frontend Developer | NextGen Media\n"
        "March 2022 - Present\n"
        "- Built React components\n"
        "- Mentored junior devs\n"
        "Frontend Developer | WebStudio\n"
        "January 2020 - February 2022\n"
        "- Built client websites using TypeScript and CSS\n"
        "Education\n"
        "Bachelor of Science in Information Technology, University of Illinois, 2019\n"
        "Skills\n"
        "React, TypeScript, Next.js, HTML5, CSS3, Tailwind CSS\n"
    )
    page2.insert_text((50, 60), text2, fontsize=10)
    pdf2_path = RESUMES_DIR / "compact_no_blanks.pdf"
    doc2.save(str(pdf2_path))
    doc2.close()

    gt2 = {
        "resume_id": "compact_no_blanks",
        "source_file": "compact_no_blanks.pdf",
        "expected": {
            "personal_info": {
                "name": "Bob Williams",
                "email": "bob.williams@email.com",
                "phone": "+1 555 345 6789",
                "location": "Chicago, USA"
            },
            "professional_summary": "Frontend Engineer focused on modern React and TypeScript.",
            "skills": ["React", "TypeScript", "Next.js", "HTML5", "CSS3", "Tailwind CSS"],
            "experience": [
                {
                    "job_title": "Lead Frontend Developer",
                    "company": "NextGen Media",
                    "start_date": "2022-03",
                    "end_date": None,
                    "is_current": True
                },
                {
                    "job_title": "Frontend Developer",
                    "company": "WebStudio",
                    "start_date": "2020-01",
                    "end_date": "2022-02",
                    "is_current": None
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Information Technology",
                    "institution": "University of Illinois",
                    "graduation_year": 2019
                }
            ],
            "raw_text": text2
        }
    }
    with open(GROUND_TRUTH_DIR / "compact_no_blanks.json", "w", encoding="utf-8") as f:
        json.dump(gt2, f, indent=2)

    # 3. skills_heavy.pdf
    doc3 = fitz.open()
    page3 = doc3.new_page()
    text3 = (
        "Carol Martinez\n"
        "carol.m@datahub.io | +1 555 987 6543 | Austin, USA\n\n"
        "Professional Summary\n"
        "Full-stack and DevOps engineer with experience in cloud infrastructure and data pipelines.\n\n"
        "Work Experience\n"
        "DevOps Engineer, DataFlow Systems\n"
        "2021 - Present\n"
        "- Managed Kubernetes clusters, Terraform infrastructure, and Docker deployments\n\n"
        "Education\n"
        "Bachelor of Science in Computer Engineering, UT Austin, 2020\n\n"
        "Skills\n"
        "Python, Go, JavaScript, TypeScript, React, Node.js, Docker, Kubernetes, AWS, GCP, Azure, PostgreSQL, MongoDB, Redis, GraphQL, Linux, Git, Jenkins, Terraform, Kafka"
    )
    page3.insert_text((50, 60), text3, fontsize=10)
    pdf3_path = RESUMES_DIR / "skills_heavy.pdf"
    doc3.save(str(pdf3_path))
    doc3.close()

    gt3 = {
        "resume_id": "skills_heavy",
        "source_file": "skills_heavy.pdf",
        "expected": {
            "personal_info": {
                "name": "Carol Martinez",
                "email": "carol.m@datahub.io",
                "phone": "+1 555 987 6543",
                "location": "Austin, USA"
            },
            "skills": [
                "Python", "Go", "JavaScript", "TypeScript", "React", "Node.js", "Docker",
                "Kubernetes", "AWS", "GCP", "Azure", "PostgreSQL", "MongoDB", "Redis",
                "GraphQL", "Linux", "Git", "Jenkins", "Terraform", "Kafka"
            ],
            "experience": [
                {
                    "job_title": "DevOps Engineer",
                    "company": "DataFlow Systems",
                    "start_date": "2021",
                    "end_date": None,
                    "is_current": True
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Engineering",
                    "institution": "UT Austin",
                    "graduation_year": 2020
                }
            ],
            "raw_text": text3
        }
    }
    with open(GROUND_TRUTH_DIR / "skills_heavy.json", "w", encoding="utf-8") as f:
        json.dump(gt3, f, indent=2)

    # 4. education_focused.docx
    doc4 = Document()
    doc4.add_heading("David Chen", level=0)
    doc4.add_paragraph("david.chen@mit.edu | +1 555 456 7890 | Boston, USA")
    doc4.add_heading("Professional Summary", level=1)
    doc4.add_paragraph("Machine learning researcher and software engineer.")
    doc4.add_heading("Work Experience", level=1)
    p_exp = doc4.add_paragraph("Research Assistant, AI Lab\nSeptember 2021 - May 2023\nConducted NLP experiments using PyTorch.")
    doc4.add_heading("Education", level=1)
    doc4.add_paragraph("PhD in Artificial Intelligence, MIT, 2024\nMaster of Science in Computer Science, Carnegie Mellon University, 2021\nBachelor of Science in Mathematics, Harvard University, 2019")
    doc4.add_heading("Skills", level=1)
    doc4.add_paragraph("Python, PyTorch, TensorFlow, Scikit-learn, Pandas, NumPy, C++, Git")
    doc4.add_heading("Certifications", level=1)
    doc4.add_paragraph("Deep Learning Specialization (DeepLearning.AI, 2020)")
    doc4.add_heading("Projects", level=1)
    doc4.add_paragraph("Transformer-Parser: Neural dependency parser built in PyTorch.")
    docx4_path = RESUMES_DIR / "education_focused.docx"
    doc4.save(str(docx4_path))

    gt4 = {
        "resume_id": "education_focused",
        "source_file": "education_focused.docx",
        "expected": {
            "personal_info": {
                "name": "David Chen",
                "email": "david.chen@mit.edu",
                "phone": "+1 555 456 7890",
                "location": "Boston, USA"
            },
            "professional_summary": "Machine learning researcher and software engineer.",
            "skills": ["Python", "PyTorch", "TensorFlow", "Scikit-learn", "Pandas", "NumPy", "C++", "Git"],
            "experience": [
                {
                    "job_title": "Research Assistant",
                    "company": "AI Lab",
                    "start_date": "2021-09",
                    "end_date": "2023-05"
                }
            ],
            "education": [
                {
                    "degree": "PhD in Artificial Intelligence",
                    "institution": "MIT",
                    "graduation_year": 2024
                }
            ],
            "certifications": [
                {
                    "name": "Deep Learning Specialization",
                    "issuer": "DeepLearning.AI",
                    "date": "2020"
                }
            ],
            "projects": [
                {
                    "name": "Transformer-Parser",
                    "description": "Neural dependency parser built in PyTorch."
                }
            ]
        }
    }
    with open(GROUND_TRUTH_DIR / "education_focused.json", "w", encoding="utf-8") as f:
        json.dump(gt4, f, indent=2)

    # 5. table_resume.docx
    doc5 = Document()
    t_header = doc5.add_table(rows=1, cols=2)
    t_header.rows[0].cells[0].text = "Eva Green\neva.green@techcorp.com\n+1 555 678 9012"
    t_header.rows[0].cells[1].text = "Seattle, USA\nhttps://github.com/evagreen"

    doc5.add_heading("Professional Summary", level=1)
    doc5.add_paragraph("Full Stack Developer with 4 years building scalable web services.")

    doc5.add_heading("Work Experience", level=1)
    p_exp5 = doc5.add_paragraph("Full Stack Developer, TechCorp\nFebruary 2021 - Present\n- Built microservices using Node.js and Express\n- Developed frontend in React")

    doc5.add_heading("Education", level=1)
    doc5.add_paragraph("Bachelor of Science in Software Engineering, University of Washington, 2020")

    doc5.add_heading("Skills", level=1)
    t_skills = doc5.add_table(rows=1, cols=2)
    t_skills.rows[0].cells[0].text = "JavaScript, TypeScript, React, HTML5, CSS3"
    t_skills.rows[0].cells[1].text = "Node.js, Express, PostgreSQL, MongoDB, Docker"

    docx5_path = RESUMES_DIR / "table_resume.docx"
    doc5.save(str(docx5_path))

    gt5 = {
        "resume_id": "table_resume",
        "source_file": "table_resume.docx",
        "expected": {
            "personal_info": {
                "name": "Eva Green",
                "email": "eva.green@techcorp.com",
                "phone": "+1 555 678 9012",
                "location": "Seattle, USA",
                "github": "https://github.com/evagreen"
            },
            "professional_summary": "Full Stack Developer with 4 years building scalable web services.",
            "skills": [
                "JavaScript", "TypeScript", "React", "HTML5", "CSS3",
                "Node.js", "Express", "PostgreSQL", "MongoDB", "Docker"
            ],
            "experience": [
                {
                    "job_title": "Full Stack Developer",
                    "company": "TechCorp",
                    "start_date": "2021-02",
                    "end_date": None,
                    "is_current": True
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Software Engineering",
                    "institution": "University of Washington",
                    "graduation_year": 2020
                }
            ]
        }
    }
    with open(GROUND_TRUTH_DIR / "table_resume.json", "w", encoding="utf-8") as f:
        json.dump(gt5, f, indent=2)

    print("Successfully generated 5 synthetic resumes and ground truth JSON files.")

if __name__ == "__main__":
    generate_fixtures()

