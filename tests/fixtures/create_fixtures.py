import json
import re
from pathlib import Path
import fitz  # PyMuPDF
from docx import Document
from PIL import Image

FIXTURES_DIR = Path(__file__).resolve().parent
RESUMES_DIR = FIXTURES_DIR / "resumes"
GROUND_TRUTH_DIR = FIXTURES_DIR / "ground_truth"
BIO_DIR = FIXTURES_DIR / "bio"

def generate_fixtures():
    RESUMES_DIR.mkdir(parents=True, exist_ok=True)
    GROUND_TRUTH_DIR.mkdir(parents=True, exist_ok=True)
    BIO_DIR.mkdir(parents=True, exist_ok=True)

    # ==========================================
    # 1. simple_single_column.pdf
    # ==========================================
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

    # ==========================================
    # 2. compact_no_blanks.pdf
    # ==========================================
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

    # ==========================================
    # 3. skills_heavy.pdf
    # ==========================================
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

    # ==========================================
    # 4. education_focused.docx
    # ==========================================
    doc4 = Document()
    doc4.add_heading("David Chen", level=0)
    doc4.add_paragraph("david.chen@mit.edu | +1 555 456 7890 | Boston, USA")
    doc4.add_heading("Professional Summary", level=1)
    doc4.add_paragraph("Machine learning researcher and software engineer.")
    doc4.add_heading("Work Experience", level=1)
    doc4.add_paragraph("Research Assistant, AI Lab\nSeptember 2021 - May 2023\nConducted NLP experiments using PyTorch.")
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

    # ==========================================
    # 5. table_resume.docx
    # ==========================================
    doc5 = Document()
    t_header = doc5.add_table(rows=1, cols=2)
    t_header.rows[0].cells[0].text = "Eva Green\neva.green@techcorp.com\n+1 555 678 9012"
    t_header.rows[0].cells[1].text = "Seattle, USA\nhttps://github.com/evagreen"

    doc5.add_heading("Professional Summary", level=1)
    doc5.add_paragraph("Full Stack Developer with 4 years building scalable web services.")

    doc5.add_heading("Work Experience", level=1)
    doc5.add_paragraph("Full Stack Developer, TechCorp\nFebruary 2021 - Present\n- Built microservices using Node.js and Express\n- Developed frontend in React")

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

    # ==========================================
    # 6. single_col_datascience.pdf
    # ==========================================
    doc6 = fitz.open()
    page6 = doc6.new_page()
    text6 = (
        "Elena Rostova\n"
        "elena.rostova@datascience.org | +1 555 111 2233 | New York, USA\n\n"
        "Professional Summary\n"
        "Lead Data Scientist with 6 years experience building production ML pipelines and predictive models.\n\n"
        "Work Experience\n"
        "Lead Data Scientist, DataCorp\n"
        "March 2021 - Present\n"
        "- Built real-time recommendation engine using Python and PyTorch\n"
        "- Deployed models to AWS with Docker\n\n"
        "Data Scientist, AnalyticsHub\n"
        "July 2018 - February 2021\n"
        "- Developed churn prediction models using Scikit-learn and Pandas\n"
        "- Automated ETL pipelines with SQL\n\n"
        "Education\n"
        "Master of Science in Data Science, Columbia University, 2018\n\n"
        "Skills\n"
        "Python, PyTorch, Pandas, Scikit-learn, SQL, AWS, Docker, Git, Linux\n\n"
        "Certifications\n"
        "AWS Certified Machine Learning Specialist (Amazon, 2022)"
    )
    page6.insert_text((50, 60), text6, fontsize=10)
    doc6.save(str(RESUMES_DIR / "single_col_datascience.pdf"))
    doc6.close()

    gt6 = {
        "resume_id": "single_col_datascience",
        "source_file": "single_col_datascience.pdf",
        "expected": {
            "personal_info": {
                "name": "Elena Rostova",
                "email": "elena.rostova@datascience.org",
                "phone": "+1 555 111 2233",
                "location": "New York, USA"
            },
            "professional_summary": "Lead Data Scientist with 6 years experience building production ML pipelines and predictive models.",
            "skills": ["Python", "PyTorch", "Pandas", "Scikit-learn", "SQL", "AWS", "Docker", "Git", "Linux"],
            "experience": [
                {
                    "job_title": "Lead Data Scientist",
                    "company": "DataCorp",
                    "start_date": "2021-03",
                    "end_date": None,
                    "is_current": True
                },
                {
                    "job_title": "Data Scientist",
                    "company": "AnalyticsHub",
                    "start_date": "2018-07",
                    "end_date": "2021-02",
                    "is_current": None
                }
            ],
            "education": [
                {
                    "degree": "Master of Science in Data Science",
                    "institution": "Columbia University",
                    "graduation_year": 2018
                }
            ],
            "certifications": [
                {
                    "name": "AWS Certified Machine Learning Specialist",
                    "issuer": "Amazon",
                    "date": "2022"
                }
            ],
            "raw_text": text6
        }
    }
    with open(GROUND_TRUTH_DIR / "single_col_datascience.json", "w", encoding="utf-8") as f:
        json.dump(gt6, f, indent=2)

    # ==========================================
    # 7. single_col_devops.pdf
    # ==========================================
    doc7 = fitz.open()
    page7 = doc7.new_page()
    text7 = (
        "Marcus Vance\n"
        "marcus.vance@cloudinfra.net | +1 555 222 3344 | Seattle, USA\n\n"
        "Professional Summary\n"
        "Site Reliability Engineer specializing in Kubernetes, Terraform, and cloud observability.\n\n"
        "Work Experience\n"
        "Senior SRE, CloudMatrix\n"
        "May 2020 - Present\n"
        "- Architected multi-region Kubernetes clusters with Terraform\n"
        "- Built monitoring dashboards using Prometheus and Grafana\n\n"
        "DevOps Engineer, InfraScale\n"
        "September 2017 - April 2020\n"
        "- Automated deployment pipelines with Ansible and Jenkins\n"
        "- Managed Linux servers on AWS\n\n"
        "Education\n"
        "Bachelor of Science in Computer Science, University of Washington, 2017\n\n"
        "Skills\n"
        "Kubernetes, Docker, Terraform, Prometheus, Grafana, Ansible, AWS, Linux, Python, Git, Jenkins"
    )
    page7.insert_text((50, 60), text7, fontsize=10)
    doc7.save(str(RESUMES_DIR / "single_col_devops.pdf"))
    doc7.close()

    gt7 = {
        "resume_id": "single_col_devops",
        "source_file": "single_col_devops.pdf",
        "expected": {
            "personal_info": {
                "name": "Marcus Vance",
                "email": "marcus.vance@cloudinfra.net",
                "phone": "+1 555 222 3344",
                "location": "Seattle, USA"
            },
            "professional_summary": "Site Reliability Engineer specializing in Kubernetes, Terraform, and cloud observability.",
            "skills": ["Kubernetes", "Docker", "Terraform", "Prometheus", "Grafana", "Ansible", "AWS", "Linux", "Python", "Git", "Jenkins"],
            "experience": [
                {
                    "job_title": "Senior SRE",
                    "company": "CloudMatrix",
                    "start_date": "2020-05",
                    "end_date": None,
                    "is_current": True
                },
                {
                    "job_title": "DevOps Engineer",
                    "company": "InfraScale",
                    "start_date": "2017-09",
                    "end_date": "2020-04",
                    "is_current": None
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "institution": "University of Washington",
                    "graduation_year": 2017
                }
            ],
            "raw_text": text7
        }
    }
    with open(GROUND_TRUTH_DIR / "single_col_devops.json", "w", encoding="utf-8") as f:
        json.dump(gt7, f, indent=2)

    # ==========================================
    # 8. single_col_mobile.pdf
    # ==========================================
    doc8 = fitz.open()
    page8 = doc8.new_page()
    text8 = (
        "Sophia Martinez\n"
        "sophia.m@mobiledev.io | +1 555 333 4455 | Austin, USA\n\n"
        "Professional Summary\n"
        "Mobile Applications Developer with expertise in iOS, Android, and cross-platform frameworks.\n\n"
        "Work Experience\n"
        "Senior Mobile Engineer, AppWorks\n"
        "August 2021 - Present\n"
        "- Developed cross-platform applications in Flutter and React Native\n"
        "- Integrated REST and GraphQL APIs with Firebase backends\n\n"
        "iOS Developer, SwiftCraft\n"
        "January 2019 - July 2021\n"
        "- Built native iOS applications using Swift\n\n"
        "Education\n"
        "Bachelor of Science in Software Development, UT Austin, 2018\n\n"
        "Skills\n"
        "Swift, Kotlin, Flutter, React Native, iOS, Android, Git, REST, GraphQL, Firebase"
    )
    page8.insert_text((50, 60), text8, fontsize=10)
    doc8.save(str(RESUMES_DIR / "single_col_mobile.pdf"))
    doc8.close()

    gt8 = {
        "resume_id": "single_col_mobile",
        "source_file": "single_col_mobile.pdf",
        "expected": {
            "personal_info": {
                "name": "Sophia Martinez",
                "email": "sophia.m@mobiledev.io",
                "phone": "+1 555 333 4455",
                "location": "Austin, USA"
            },
            "professional_summary": "Mobile Applications Developer with expertise in iOS, Android, and cross-platform frameworks.",
            "skills": ["Swift", "Kotlin", "Flutter", "React Native", "iOS", "Android", "Git", "REST", "GraphQL", "Firebase"],
            "experience": [
                {
                    "job_title": "Senior Mobile Engineer",
                    "company": "AppWorks",
                    "start_date": "2021-08",
                    "end_date": None,
                    "is_current": True
                },
                {
                    "job_title": "iOS Developer",
                    "company": "SwiftCraft",
                    "start_date": "2019-01",
                    "end_date": "2021-07",
                    "is_current": None
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Software Development",
                    "institution": "UT Austin",
                    "graduation_year": 2018
                }
            ],
            "raw_text": text8
        }
    }
    with open(GROUND_TRUTH_DIR / "single_col_mobile.json", "w", encoding="utf-8") as f:
        json.dump(gt8, f, indent=2)

    # ==========================================
    # 9. twocol_software_eng.pdf (Two-column layout)
    # ==========================================
    doc9 = fitz.open()
    page9 = doc9.new_page(width=595, height=842)
    # Header block across top
    header9 = (
        "Alex Rivera\n"
        "alex.rivera@fullstack.dev | +1 555 444 5566 | Denver, USA\n"
        "Professional Summary\n"
        "Full Stack Engineer with 5 years experience in TypeScript, React, and microservices."
    )
    page9.insert_text((50, 50), header9, fontsize=10)
    # Left column: Education & Skills
    left9 = (
        "Education\n"
        "Bachelor of Science in Computer Science, University of Colorado, 2019\n\n"
        "Skills\n"
        "TypeScript, React, Node.js, Next.js, PostgreSQL, Docker, Redis, Git, Linux\n\n"
        "Languages\n"
        "English, Spanish"
    )
    page9.insert_text((50, 140), left9, fontsize=10)
    # Right column: Experience
    right9 = (
        "Work Experience\n"
        "Senior Full Stack Developer | Apex Solutions\n"
        "January 2022 - Present\n"
        "- Built Next.js web applications with React and TypeScript\n"
        "- Optimized PostgreSQL and Redis cache layers\n\n"
        "Full Stack Developer | Digital Forge\n"
        "June 2019 - December 2021\n"
        "- Developed Node.js REST APIs and React frontends"
    )
    page9.insert_text((270, 140), right9, fontsize=10)
    doc9.save(str(RESUMES_DIR / "twocol_software_eng.pdf"))
    doc9.close()

    gt9 = {
        "resume_id": "twocol_software_eng",
        "source_file": "twocol_software_eng.pdf",
        "expected": {
            "personal_info": {
                "name": "Alex Rivera",
                "email": "alex.rivera@fullstack.dev",
                "phone": "+1 555 444 5566",
                "location": "Denver, USA"
            },
            "professional_summary": "Full Stack Engineer with 5 years experience in TypeScript, React, and microservices.",
            "skills": ["TypeScript", "React", "Node.js", "Next.js", "PostgreSQL", "Docker", "Redis", "Git", "Linux"],
            "languages": ["English", "Spanish"],
            "experience": [
                {
                    "job_title": "Senior Full Stack Developer",
                    "company": "Apex Solutions",
                    "start_date": "2022-01",
                    "end_date": None,
                    "is_current": True
                },
                {
                    "job_title": "Full Stack Developer",
                    "company": "Digital Forge",
                    "start_date": "2019-06",
                    "end_date": "2021-12",
                    "is_current": None
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "institution": "University of Colorado",
                    "graduation_year": 2019
                }
            ]
        }
    }
    with open(GROUND_TRUTH_DIR / "twocol_software_eng.json", "w", encoding="utf-8") as f:
        json.dump(gt9, f, indent=2)

    # ==========================================
    # 10. twocol_product_mgr.pdf (Two-column layout)
    # ==========================================
    doc10 = fitz.open()
    page10 = doc10.new_page(width=595, height=842)
    header10 = (
        "Rachel Kim\n"
        "rachel.kim@productlead.com | +1 555 555 6677 | Chicago, USA\n"
        "Professional Summary\n"
        "Technical Product Manager with background in software development and agile roadmapping."
    )
    page10.insert_text((50, 50), header10, fontsize=10)
    left10 = (
        "Education\n"
        "Master of Business Administration, Northwestern University, 2020\n\n"
        "Skills\n"
        "Agile, Scrum, Jira, SQL, Python, Figma, Git"
    )
    page10.insert_text((50, 140), left10, fontsize=10)
    right10 = (
        "Work Experience\n"
        "Lead Product Manager, InnovateX\n"
        "April 2021 - Present\n"
        "- Spearheaded product strategy for enterprise SaaS platforms\n"
        "- Defined sprint backlogs and user stories using Jira\n\n"
        "Technical Product Manager, SprintLabs\n"
        "February 2018 - March 2021\n"
        "- Led cross-functional engineering teams using Scrum and Agile"
    )
    page10.insert_text((270, 140), right10, fontsize=10)
    doc10.save(str(RESUMES_DIR / "twocol_product_mgr.pdf"))
    doc10.close()

    gt10 = {
        "resume_id": "twocol_product_mgr",
        "source_file": "twocol_product_mgr.pdf",
        "expected": {
            "personal_info": {
                "name": "Rachel Kim",
                "email": "rachel.kim@productlead.com",
                "phone": "+1 555 555 6677",
                "location": "Chicago, USA"
            },
            "professional_summary": "Technical Product Manager with background in software development and agile roadmapping.",
            "skills": ["Agile", "Scrum", "Jira", "SQL", "Python", "Figma", "Git"],
            "experience": [
                {
                    "job_title": "Lead Product Manager",
                    "company": "InnovateX",
                    "start_date": "2021-04",
                    "end_date": None,
                    "is_current": True
                },
                {
                    "job_title": "Technical Product Manager",
                    "company": "SprintLabs",
                    "start_date": "2018-02",
                    "end_date": "2021-03",
                    "is_current": None
                }
            ],
            "education": [
                {
                    "degree": "Master of Business Administration",
                    "institution": "Northwestern University",
                    "graduation_year": 2020
                }
            ]
        }
    }
    with open(GROUND_TRUTH_DIR / "twocol_product_mgr.json", "w", encoding="utf-8") as f:
        json.dump(gt10, f, indent=2)

    # ==========================================
    # 11. twocol_data_analyst.pdf (Two-column layout)
    # ==========================================
    doc11 = fitz.open()
    page11 = doc11.new_page(width=595, height=842)
    header11 = (
        "James O'Connor\n"
        "james.oconnor@analytics.org | +1 555 666 7788 | Boston, USA\n"
        "Professional Summary\n"
        "Senior Data Analyst delivering actionable business intelligence and dashboards."
    )
    page11.insert_text((50, 50), header11, fontsize=10)
    left11 = (
        "Education\n"
        "Bachelor of Science in Statistics, Boston University, 2019\n\n"
        "Skills\n"
        "SQL, Python, Tableau, Power BI, Excel, Snowflake, dbt, Looker, Git"
    )
    page11.insert_text((50, 140), left11, fontsize=10)
    right11 = (
        "Work Experience\n"
        "Senior Data Analyst, MetricFlow\n"
        "October 2021 - Present\n"
        "- Built executive dashboards in Tableau and Power BI\n"
        "- Transformed enterprise data models with Snowflake and dbt\n\n"
        "Business Data Analyst, InsightCorp\n"
        "May 2019 - September 2021\n"
        "- Analyzed sales metrics using SQL and Python"
    )
    page11.insert_text((270, 140), right11, fontsize=10)
    doc11.save(str(RESUMES_DIR / "twocol_data_analyst.pdf"))
    doc11.close()

    gt11 = {
        "resume_id": "twocol_data_analyst",
        "source_file": "twocol_data_analyst.pdf",
        "expected": {
            "personal_info": {
                "name": "James O'Connor",
                "email": "james.oconnor@analytics.org",
                "phone": "+1 555 666 7788",
                "location": "Boston, USA"
            },
            "professional_summary": "Senior Data Analyst delivering actionable business intelligence and dashboards.",
            "skills": ["SQL", "Python", "Tableau", "Power BI", "Excel", "Snowflake", "dbt", "Looker", "Git"],
            "experience": [
                {
                    "job_title": "Senior Data Analyst",
                    "company": "MetricFlow",
                    "start_date": "2021-10",
                    "end_date": None,
                    "is_current": True
                },
                {
                    "job_title": "Business Data Analyst",
                    "company": "InsightCorp",
                    "start_date": "2019-05",
                    "end_date": "2021-09",
                    "is_current": None
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Statistics",
                    "institution": "Boston University",
                    "graduation_year": 2019
                }
            ]
        }
    }
    with open(GROUND_TRUTH_DIR / "twocol_data_analyst.json", "w", encoding="utf-8") as f:
        json.dump(gt11, f, indent=2)

    # ==========================================
    # 12. twocol_cloud_architect.pdf (Two-column layout)
    # ==========================================
    doc12 = fitz.open()
    page12 = doc12.new_page(width=595, height=842)
    header12 = (
        "Vikram Patel\n"
        "vikram.patel@cloudarch.com | +1 555 777 8899 | San Jose, USA\n"
        "Professional Summary\n"
        "Cloud Solutions Architect designing resilient enterprise architectures on AWS and Azure."
    )
    page12.insert_text((50, 50), header12, fontsize=10)
    left12 = (
        "Education\n"
        "Master of Science in Computer Engineering, San Jose State University, 2017\n\n"
        "Skills\n"
        "AWS, Azure, GCP, Terraform, Kubernetes, Docker, Python, Linux, Git\n\n"
        "Certifications\n"
        "AWS Certified Solutions Architect (Amazon, 2021)"
    )
    page12.insert_text((50, 140), left12, fontsize=10)
    right12 = (
        "Work Experience\n"
        "Principal Cloud Architect, EnterpriseCloud\n"
        "June 2021 - Present\n"
        "- Designed hybrid cloud migrations on AWS and Azure\n"
        "- Standardized infrastructure as code using Terraform\n\n"
        "Senior Cloud Engineer, SkyTech\n"
        "August 2017 - May 2021\n"
        "- Built automated Kubernetes clusters and microservices"
    )
    page12.insert_text((270, 140), right12, fontsize=10)
    doc12.save(str(RESUMES_DIR / "twocol_cloud_architect.pdf"))
    doc12.close()

    gt12 = {
        "resume_id": "twocol_cloud_architect",
        "source_file": "twocol_cloud_architect.pdf",
        "expected": {
            "personal_info": {
                "name": "Vikram Patel",
                "email": "vikram.patel@cloudarch.com",
                "phone": "+1 555 777 8899",
                "location": "San Jose, USA"
            },
            "professional_summary": "Cloud Solutions Architect designing resilient enterprise architectures on AWS and Azure.",
            "skills": ["AWS", "Azure", "GCP", "Terraform", "Kubernetes", "Docker", "Python", "Linux", "Git"],
            "experience": [
                {
                    "job_title": "Principal Cloud Architect",
                    "company": "EnterpriseCloud",
                    "start_date": "2021-06",
                    "end_date": None,
                    "is_current": True
                },
                {
                    "job_title": "Senior Cloud Engineer",
                    "company": "SkyTech",
                    "start_date": "2017-08",
                    "end_date": "2021-05",
                    "is_current": None
                }
            ],
            "education": [
                {
                    "degree": "Master of Science in Computer Engineering",
                    "institution": "San Jose State University",
                    "graduation_year": 2017
                }
            ],
            "certifications": [
                {
                    "name": "AWS Certified Solutions Architect",
                    "issuer": "Amazon",
                    "date": "2021"
                }
            ]
        }
    }
    with open(GROUND_TRUTH_DIR / "twocol_cloud_architect.json", "w", encoding="utf-8") as f:
        json.dump(gt12, f, indent=2)

    # ==========================================
    # 13. multipage_senior_architect.pdf (2 pages)
    # ==========================================
    doc13 = fitz.open()
    p13_1 = doc13.new_page()
    text13_1 = (
        "Jonathan Sterling\n"
        "j.sterling@enterprise.io | +1 555 888 9900 | New York, USA\n\n"
        "Professional Summary\n"
        "Enterprise Software Architect with over 12 years experience leading distributed systems engineering.\n\n"
        "Work Experience\n"
        "Chief Enterprise Architect, GlobalFinancial\n"
        "January 2020 - Present\n"
        "- Directed architectural transformation to event-driven microservices\n"
        "- Mentored 40+ engineers across 5 international agile teams\n\n"
        "Principal Architect, TechVenture Partners\n"
        "April 2015 - December 2019\n"
        "- Designed high-throughput trading platforms using Java and Kafka"
    )
    p13_1.insert_text((50, 60), text13_1, fontsize=10)

    p13_2 = doc13.new_page()
    text13_2 = (
        "Work Experience (Continued)\n"
        "Senior Software Engineer, FinEdge Systems\n"
        "June 2012 - March 2015\n"
        "- Developed backend financial services in Java and SQL\n\n"
        "Education\n"
        "Master of Science in Computer Science, Cornell University, 2012\n\n"
        "Skills\n"
        "Java, Python, Go, Kafka, Kubernetes, Docker, AWS, PostgreSQL, Redis, Git, Linux\n\n"
        "Certifications\n"
        "AWS Certified Solutions Architect (Amazon, 2020)"
    )
    p13_2.insert_text((50, 60), text13_2, fontsize=10)
    doc13.save(str(RESUMES_DIR / "multipage_senior_architect.pdf"))
    doc13.close()

    gt13 = {
        "resume_id": "multipage_senior_architect",
        "source_file": "multipage_senior_architect.pdf",
        "expected": {
            "personal_info": {
                "name": "Jonathan Sterling",
                "email": "j.sterling@enterprise.io",
                "phone": "+1 555 888 9900",
                "location": "New York, USA"
            },
            "professional_summary": "Enterprise Software Architect with over 12 years experience leading distributed systems engineering.",
            "skills": ["Java", "Python", "Go", "Kafka", "Kubernetes", "Docker", "AWS", "PostgreSQL", "Redis", "Git", "Linux"],
            "experience": [
                {
                    "job_title": "Chief Enterprise Architect",
                    "company": "GlobalFinancial",
                    "start_date": "2020-01",
                    "end_date": None,
                    "is_current": True
                },
                {
                    "job_title": "Principal Architect",
                    "company": "TechVenture Partners",
                    "start_date": "2015-04",
                    "end_date": "2019-12",
                    "is_current": None
                }
            ],
            "education": [
                {
                    "degree": "Master of Science in Computer Science",
                    "institution": "Cornell University",
                    "graduation_year": 2012
                }
            ],
            "certifications": [
                {
                    "name": "AWS Certified Solutions Architect",
                    "issuer": "Amazon",
                    "date": "2020"
                }
            ]
        }
    }
    with open(GROUND_TRUTH_DIR / "multipage_senior_architect.json", "w", encoding="utf-8") as f:
        json.dump(gt13, f, indent=2)

    # ==========================================
    # 14. multipage_academic_researcher.pdf (2 pages)
    # ==========================================
    doc14 = fitz.open()
    p14_1 = doc14.new_page()
    text14_1 = (
        "Catherine Thorne\n"
        "c.thorne@researchlab.edu | +1 555 999 0011 | Cambridge, USA\n\n"
        "Professional Summary\n"
        "Postdoctoral Research Scientist in Artificial Intelligence and Natural Language Processing.\n\n"
        "Work Experience\n"
        "Postdoctoral AI Researcher, MIT AI Laboratory\n"
        "September 2022 - Present\n"
        "- Researched transformer attention mechanisms and language models\n"
        "- Published papers on deep learning architectures\n\n"
        "Graduate Research Fellow, Stanford NLP Group\n"
        "September 2018 - August 2022\n"
        "- Developed neural information extraction models in PyTorch"
    )
    p14_1.insert_text((50, 60), text14_1, fontsize=10)

    p14_2 = doc14.new_page()
    text14_2 = (
        "Education\n"
        "PhD in Computer Science, Stanford University, 2022\n\n"
        "Skills\n"
        "Python, PyTorch, TensorFlow, Scikit-learn, Linux, Git, Pandas, NumPy\n\n"
        "Projects\n"
        "Neural-Summarizer: Open-source neural document summarization toolkit in PyTorch."
    )
    p14_2.insert_text((50, 60), text14_2, fontsize=10)
    doc14.save(str(RESUMES_DIR / "multipage_academic_researcher.pdf"))
    doc14.close()

    gt14 = {
        "resume_id": "multipage_academic_researcher",
        "source_file": "multipage_academic_researcher.pdf",
        "expected": {
            "personal_info": {
                "name": "Catherine Thorne",
                "email": "c.thorne@researchlab.edu",
                "phone": "+1 555 999 0011",
                "location": "Cambridge, USA"
            },
            "professional_summary": "Postdoctoral Research Scientist in Artificial Intelligence and Natural Language Processing.",
            "skills": ["Python", "PyTorch", "TensorFlow", "Scikit-learn", "Linux", "Git", "Pandas", "NumPy"],
            "experience": [
                {
                    "job_title": "Postdoctoral AI Researcher",
                    "company": "MIT AI Laboratory",
                    "start_date": "2022-09",
                    "end_date": None,
                    "is_current": True
                },
                {
                    "job_title": "Graduate Research Fellow",
                    "company": "Stanford NLP Group",
                    "start_date": "2018-09",
                    "end_date": "2022-08",
                    "is_current": None
                }
            ],
            "education": [
                {
                    "degree": "PhD in Computer Science",
                    "institution": "Stanford University",
                    "graduation_year": 2022
                }
            ],
            "projects": [
                {
                    "name": "Neural-Summarizer",
                    "description": "Open-source neural document summarization toolkit in PyTorch."
                }
            ]
        }
    }
    with open(GROUND_TRUTH_DIR / "multipage_academic_researcher.json", "w", encoding="utf-8") as f:
        json.dump(gt14, f, indent=2)

    # ==========================================
    # 15. multipage_engineering_manager.pdf (2 pages)
    # ==========================================
    doc15 = fitz.open()
    p15_1 = doc15.new_page()
    text15_1 = (
        "Daniel Roberts\n"
        "daniel.roberts@execlead.com | +1 555 012 3456 | San Francisco, USA\n\n"
        "Professional Summary\n"
        "Engineering Director with 14 years experience scaling high-growth engineering organizations.\n\n"
        "Work Experience\n"
        "Director of Engineering, ScaleFast Inc\n"
        "March 2021 - Present\n"
        "- Managed 3 engineering directors and 35 software developers\n"
        "- Scaled platform throughput to 100M daily active requests\n\n"
        "Engineering Manager, CloudPulse\n"
        "August 2016 - February 2021\n"
        "- Led core infrastructure team responsible for Kubernetes clusters"
    )
    p15_1.insert_text((50, 60), text15_1, fontsize=10)

    p15_2 = doc15.new_page()
    text15_2 = (
        "Education\n"
        "Master of Science in Software Engineering, UC Berkeley, 2012\n\n"
        "Skills\n"
        "Go, Python, Kubernetes, Docker, PostgreSQL, AWS, Agile, Jira, Git, Linux"
    )
    p15_2.insert_text((50, 60), text15_2, fontsize=10)
    doc15.save(str(RESUMES_DIR / "multipage_engineering_manager.pdf"))
    doc15.close()

    gt15 = {
        "resume_id": "multipage_engineering_manager",
        "source_file": "multipage_engineering_manager.pdf",
        "expected": {
            "personal_info": {
                "name": "Daniel Roberts",
                "email": "daniel.roberts@execlead.com",
                "phone": "+1 555 012 3456",
                "location": "San Francisco, USA"
            },
            "professional_summary": "Engineering Director with 14 years experience scaling high-growth engineering organizations.",
            "skills": ["Go", "Python", "Kubernetes", "Docker", "PostgreSQL", "AWS", "Agile", "Jira", "Git", "Linux"],
            "experience": [
                {
                    "job_title": "Director of Engineering",
                    "company": "ScaleFast Inc",
                    "start_date": "2021-03",
                    "end_date": None,
                    "is_current": True
                },
                {
                    "job_title": "Engineering Manager",
                    "company": "CloudPulse",
                    "start_date": "2016-08",
                    "end_date": "2021-02",
                    "is_current": None
                }
            ],
            "education": [
                {
                    "degree": "Master of Science in Software Engineering",
                    "institution": "UC Berkeley",
                    "graduation_year": 2012
                }
            ]
        }
    }
    with open(GROUND_TRUTH_DIR / "multipage_engineering_manager.json", "w", encoding="utf-8") as f:
        json.dump(gt15, f, indent=2)

    # ==========================================
    # 16. docx_table_consultant.docx (Table-based DOCX)
    # ==========================================
    doc16 = Document()
    t_h16 = doc16.add_table(rows=1, cols=2)
    t_h16.rows[0].cells[0].text = "Amanda Hayes\namanda.hayes@consulting.com\n+1 555 123 7890"
    t_h16.rows[0].cells[1].text = "Atlanta, USA\nProfessional Summary:\nSenior IT Consultant delivering digital transformations and cloud architecture solutions."

    doc16.add_heading("Work Experience", level=1)
    doc16.add_paragraph("Senior Technology Consultant, Global Advisory Partners\nJuly 2020 - Present\n- Led enterprise cloud migrations on AWS and Azure")
    doc16.add_paragraph("Technology Analyst, Beacon Strategy\nJune 2017 - June 2020\n- Conducted business process automation and data analysis using Python and SQL")

    doc16.add_heading("Education", level=1)
    doc16.add_paragraph("Bachelor of Science in Information Systems, Georgia Tech, 2017")

    doc16.add_heading("Skills", level=1)
    t_s16 = doc16.add_table(rows=1, cols=2)
    t_s16.rows[0].cells[0].text = "Python, SQL, AWS, Azure, Tableau"
    t_s16.rows[0].cells[1].text = "Agile, Scrum, Jira, Git, Linux"

    docx16_path = RESUMES_DIR / "docx_table_consultant.docx"
    doc16.save(str(docx16_path))

    gt16 = {
        "resume_id": "docx_table_consultant",
        "source_file": "docx_table_consultant.docx",
        "expected": {
            "personal_info": {
                "name": "Amanda Hayes",
                "email": "amanda.hayes@consulting.com",
                "phone": "+1 555 123 7890",
                "location": "Atlanta, USA"
            },
            "professional_summary": "Senior IT Consultant delivering digital transformations and cloud architecture solutions.",
            "skills": ["Python", "SQL", "AWS", "Azure", "Tableau", "Agile", "Scrum", "Jira", "Git", "Linux"],
            "experience": [
                {
                    "job_title": "Senior Technology Consultant",
                    "company": "Global Advisory Partners",
                    "start_date": "2020-07",
                    "end_date": None,
                    "is_current": True
                },
                {
                    "job_title": "Technology Analyst",
                    "company": "Beacon Strategy",
                    "start_date": "2017-06",
                    "end_date": "2020-06",
                    "is_current": None
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Information Systems",
                    "institution": "Georgia Tech",
                    "graduation_year": 2017
                }
            ]
        }
    }
    with open(GROUND_TRUTH_DIR / "docx_table_consultant.json", "w", encoding="utf-8") as f:
        json.dump(gt16, f, indent=2)

    # ==========================================
    # 17. docx_table_qa_lead.docx (Table-based DOCX)
    # ==========================================
    doc17 = Document()
    t_h17 = doc17.add_table(rows=1, cols=2)
    t_h17.rows[0].cells[0].text = "Benjamin Cooper\nben.cooper@qalead.io\n+1 555 234 8901"
    t_h17.rows[0].cells[1].text = "Dallas, USA\nProfessional Summary:\nQA Automation Lead specializing in automated testing frameworks for web and API services."

    doc17.add_heading("Work Experience", level=1)
    doc17.add_paragraph("QA Automation Lead, Testify Systems\nJanuary 2021 - Present\n- Built end-to-end testing pipelines using Cypress and Playwright")
    doc17.add_paragraph("QA Engineer, QualiTech Labs\nMarch 2018 - December 2020\n- Automated regression suites with Selenium and Python")

    doc17.add_heading("Education", level=1)
    doc17.add_paragraph("Bachelor of Science in Computer Engineering, UT Dallas, 2018")

    doc17.add_heading("Skills", level=1)
    t_s17 = doc17.add_table(rows=1, cols=2)
    t_s17.rows[0].cells[0].text = "Selenium, Cypress, Playwright, Python, Java"
    t_s17.rows[0].cells[1].text = "Jest, Postman, CI/CD, Git, Linux, Docker"

    docx17_path = RESUMES_DIR / "docx_table_qa_lead.docx"
    doc17.save(str(docx17_path))

    gt17 = {
        "resume_id": "docx_table_qa_lead",
        "source_file": "docx_table_qa_lead.docx",
        "expected": {
            "personal_info": {
                "name": "Benjamin Cooper",
                "email": "ben.cooper@qalead.io",
                "phone": "+1 555 234 8901",
                "location": "Dallas, USA"
            },
            "professional_summary": "QA Automation Lead specializing in automated testing frameworks for web and API services.",
            "skills": ["Selenium", "Cypress", "Playwright", "Python", "Java", "Jest", "Postman", "CI/CD", "Git", "Linux", "Docker"],
            "experience": [
                {
                    "job_title": "QA Automation Lead",
                    "company": "Testify Systems",
                    "start_date": "2021-01",
                    "end_date": None,
                    "is_current": True
                },
                {
                    "job_title": "QA Engineer",
                    "company": "QualiTech Labs",
                    "start_date": "2018-03",
                    "end_date": "2020-12",
                    "is_current": None
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Engineering",
                    "institution": "UT Dallas",
                    "graduation_year": 2018
                }
            ]
        }
    }
    with open(GROUND_TRUTH_DIR / "docx_table_qa_lead.json", "w", encoding="utf-8") as f:
        json.dump(gt17, f, indent=2)

    # ==========================================
    # 18. docx_plain_sysadmin.docx (Plain DOCX)
    # ==========================================
    doc18 = Document()
    doc18.add_heading("Gregory Foster", level=0)
    doc18.add_paragraph("greg.foster@sysops.org | +1 555 345 9012 | Phoenix, USA")
    doc18.add_heading("Professional Summary", level=1)
    doc18.add_paragraph("Linux Systems Administrator with 8 years managing high-availability server clusters.")
    doc18.add_heading("Work Experience", level=1)
    doc18.add_paragraph("Senior Systems Administrator, CoreHost Networks\nNovember 2019 - Present\n- Maintained 500+ Linux servers with Ansible automation\n- Configured NGINX and Apache web servers")
    doc18.add_paragraph("Systems Administrator, NetSolutions\nApril 2016 - October 2019\n- Managed VMware virtual infrastructure and DNS services")
    doc18.add_heading("Education", level=1)
    doc18.add_paragraph("Bachelor of Science in Information Technology, Arizona State University, 2016")
    doc18.add_heading("Skills", level=1)
    doc18.add_paragraph("Linux, Bash, Ansible, VMware, DNS, NGINX, Apache, Python, Git")

    docx18_path = RESUMES_DIR / "docx_plain_sysadmin.docx"
    doc18.save(str(docx18_path))

    gt18 = {
        "resume_id": "docx_plain_sysadmin",
        "source_file": "docx_plain_sysadmin.docx",
        "expected": {
            "personal_info": {
                "name": "Gregory Foster",
                "email": "greg.foster@sysops.org",
                "phone": "+1 555 345 9012",
                "location": "Phoenix, USA"
            },
            "professional_summary": "Linux Systems Administrator with 8 years managing high-availability server clusters.",
            "skills": ["Linux", "Bash", "Ansible", "VMware", "DNS", "NGINX", "Apache", "Python", "Git"],
            "experience": [
                {
                    "job_title": "Senior Systems Administrator",
                    "company": "CoreHost Networks",
                    "start_date": "2019-11",
                    "end_date": None,
                    "is_current": True
                },
                {
                    "job_title": "Systems Administrator",
                    "company": "NetSolutions",
                    "start_date": "2016-04",
                    "end_date": "2019-10",
                    "is_current": None
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Information Technology",
                    "institution": "Arizona State University",
                    "graduation_year": 2016
                }
            ]
        }
    }
    with open(GROUND_TRUTH_DIR / "docx_plain_sysadmin.json", "w", encoding="utf-8") as f:
        json.dump(gt18, f, indent=2)

    # ==========================================
    # 19. docx_plain_security_eng.docx (Plain DOCX)
    # ==========================================
    doc19 = Document()
    doc19.add_heading("Morgan Taylor", level=0)
    doc19.add_paragraph("morgan.taylor@secops.io | +1 555 456 0123 | San Diego, USA")
    doc19.add_heading("Professional Summary", level=1)
    doc19.add_paragraph("Information Security Analyst specializing in threat detection, SIEM, and vulnerability analysis.")
    doc19.add_heading("Work Experience", level=1)
    doc19.add_paragraph("Information Security Analyst, CyberGuard Systems\nMay 2021 - Present\n- Monitored security alerts using Splunk SIEM\n- Conducted vulnerability assessments using Wireshark")
    doc19.add_paragraph("Junior Security Analyst, SecureNet\nFebruary 2019 - April 2021\n- Administered IAM policies and audited user permissions")
    doc19.add_heading("Education", level=1)
    doc19.add_paragraph("Bachelor of Science in Cybersecurity, San Diego State University, 2019")
    doc19.add_heading("Skills", level=1)
    doc19.add_paragraph("Cybersecurity, SIEM, Splunk, Wireshark, Penetration Testing, IAM, OWASP, Linux, Python, Git")

    docx19_path = RESUMES_DIR / "docx_plain_security_eng.docx"
    doc19.save(str(docx19_path))

    gt19 = {
        "resume_id": "docx_plain_security_eng",
        "source_file": "docx_plain_security_eng.docx",
        "expected": {
            "personal_info": {
                "name": "Morgan Taylor",
                "email": "morgan.taylor@secops.io",
                "phone": "+1 555 456 0123",
                "location": "San Diego, USA"
            },
            "professional_summary": "Information Security Analyst specializing in threat detection, SIEM, and vulnerability analysis.",
            "skills": ["Cybersecurity", "SIEM", "Splunk", "Wireshark", "Penetration Testing", "IAM", "OWASP", "Linux", "Python", "Git"],
            "experience": [
                {
                    "job_title": "Information Security Analyst",
                    "company": "CyberGuard Systems",
                    "start_date": "2021-05",
                    "end_date": None,
                    "is_current": True
                },
                {
                    "job_title": "Junior Security Analyst",
                    "company": "SecureNet",
                    "start_date": "2019-02",
                    "end_date": "2021-04",
                    "is_current": None
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Cybersecurity",
                    "institution": "San Diego State University",
                    "graduation_year": 2019
                }
            ]
        }
    }
    with open(GROUND_TRUTH_DIR / "docx_plain_security_eng.json", "w", encoding="utf-8") as f:
        json.dump(gt19, f, indent=2)

    # ==========================================
    # 20. scanned_analyst.pdf (Scanned image PDF)
    # ==========================================
    temp_doc20 = fitz.open()
    temp_page20 = temp_doc20.new_page(width=595, height=842)
    text20 = (
        "Samantha Miller\n"
        "samantha.miller@bizsystems.net | +1 555 567 1234 | Portland, USA\n\n"
        "Professional Summary\n"
        "Business Systems Analyst bridging technical engineering and business stakeholders.\n\n"
        "Work Experience\n"
        "Senior Business Analyst, DataBridge Systems\n"
        "June 2021 - Present\n"
        "- Gathered technical requirements and built SQL models\n\n"
        "Education\n"
        "Bachelor of Science in Information Systems, Portland State University, 2020\n\n"
        "Skills\n"
        "SQL, Python, Tableau, Agile, Jira, Excel, Git"
    )
    temp_page20.insert_text((50, 60), text20, fontsize=12)
    pix20 = temp_page20.get_pixmap(dpi=200)
    img_bytes20 = pix20.tobytes("png")
    temp_doc20.close()

    doc20 = fitz.open()
    page20 = doc20.new_page(width=595, height=842)
    page20.insert_image(page20.rect, stream=img_bytes20)
    doc20.save(str(RESUMES_DIR / "scanned_analyst.pdf"))
    doc20.close()

    gt20 = {
        "resume_id": "scanned_analyst",
        "source_file": "scanned_analyst.pdf",
        "expected": {
            "personal_info": {
                "name": "Samantha Miller",
                "email": "samantha.miller@bizsystems.net",
                "phone": "+1 555 567 1234",
                "location": "Portland, USA"
            },
            "professional_summary": "Business Systems Analyst bridging technical engineering and business stakeholders.",
            "skills": ["SQL", "Python", "Tableau", "Agile", "Jira", "Excel", "Git"],
            "experience": [
                {
                    "job_title": "Senior Business Analyst",
                    "company": "DataBridge Systems",
                    "start_date": "2021-06",
                    "end_date": None,
                    "is_current": True
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Information Systems",
                    "institution": "Portland State University",
                    "graduation_year": 2020
                }
            ],
            "raw_text": text20
        }
    }
    with open(GROUND_TRUTH_DIR / "scanned_analyst.json", "w", encoding="utf-8") as f:
        json.dump(gt20, f, indent=2)

    # ==========================================
    # 21. scanned_developer.pdf (Scanned image PDF)
    # ==========================================
    temp_doc21 = fitz.open()
    temp_page21 = temp_doc21.new_page(width=595, height=842)
    text21 = (
        "Lucas Vance\n"
        "lucas.vance@embeddedtech.org | +1 555 678 2345 | Detroit, USA\n\n"
        "Professional Summary\n"
        "Embedded Systems Developer specializing in real-time firmware and RTOS device drivers.\n\n"
        "Work Experience\n"
        "Embedded Software Engineer, AutoDrive Systems\n"
        "September 2020 - Present\n"
        "- Developed firmware drivers in C and C++ for automotive controllers\n\n"
        "Education\n"
        "Bachelor of Science in Computer Engineering, University of Michigan, 2020\n\n"
        "Skills\n"
        "C, C++, Linux, Git, RTOS, ARM, Python"
    )
    temp_page21.insert_text((50, 60), text21, fontsize=12)
    pix21 = temp_page21.get_pixmap(dpi=200)
    img_bytes21 = pix21.tobytes("png")
    temp_doc21.close()

    doc21 = fitz.open()
    page21 = doc21.new_page(width=595, height=842)
    page21.insert_image(page21.rect, stream=img_bytes21)
    doc21.save(str(RESUMES_DIR / "scanned_developer.pdf"))
    doc21.close()

    gt21 = {
        "resume_id": "scanned_developer",
        "source_file": "scanned_developer.pdf",
        "expected": {
            "personal_info": {
                "name": "Lucas Vance",
                "email": "lucas.vance@embeddedtech.org",
                "phone": "+1 555 678 2345",
                "location": "Detroit, USA"
            },
            "professional_summary": "Embedded Systems Developer specializing in real-time firmware and RTOS device drivers.",
            "skills": ["C", "C++", "Linux", "Git", "RTOS", "ARM", "Python"],
            "experience": [
                {
                    "job_title": "Embedded Software Engineer",
                    "company": "AutoDrive Systems",
                    "start_date": "2020-09",
                    "end_date": None,
                    "is_current": True
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Engineering",
                    "institution": "University of Michigan",
                    "graduation_year": 2020
                }
            ],
            "raw_text": text21
        }
    }
    with open(GROUND_TRUTH_DIR / "scanned_developer.json", "w", encoding="utf-8") as f:
        json.dump(gt21, f, indent=2)

    # ==========================================
    # 22. intl_germany_berlin.pdf (International PDF)
    # ==========================================
    doc22 = fitz.open()
    page22 = doc22.new_page()
    text22 = (
        "Johannes Neumann\n"
        "johannes.neumann@berlin-tech.de | +49 30 12345678 | Berlin, Germany\n\n"
        "Professional Summary\n"
        "Senior Software Engineer and Algorithm Researcher with background in high-performance computing.\n\n"
        "Work Experience\n"
        "Principal Software Engineer, Berlin Data Systems\n"
        "January 2021 - Present\n"
        "- Engineered microservices using Go and Docker\n\n"
        "Senior Software Developer, Munich Cloud Solutions\n"
        "April 2017 - December 2020\n"
        "- Developed distributed backend pipelines with Python and PostgreSQL\n\n"
        "Education\n"
        "PhD in Computer Science, Technical University of Munich, 2017\n\n"
        "Skills\n"
        "Python, C++, Go, Docker, Kubernetes, Linux, Git, PostgreSQL\n\n"
        "Languages\n"
        "German, English"
    )
    page22.insert_text((50, 60), text22, fontsize=10)
    doc22.save(str(RESUMES_DIR / "intl_germany_berlin.pdf"))
    doc22.close()

    gt22 = {
        "resume_id": "intl_germany_berlin",
        "source_file": "intl_germany_berlin.pdf",
        "expected": {
            "personal_info": {
                "name": "Johannes Neumann",
                "email": "johannes.neumann@berlin-tech.de",
                "phone": "+49 30 12345678",
                "location": "Berlin, Germany"
            },
            "professional_summary": "Senior Software Engineer and Algorithm Researcher with background in high-performance computing.",
            "skills": ["Python", "C++", "Go", "Docker", "Kubernetes", "Linux", "Git", "PostgreSQL"],
            "languages": ["German", "English"],
            "experience": [
                {
                    "job_title": "Principal Software Engineer",
                    "company": "Berlin Data Systems",
                    "start_date": "2021-01",
                    "end_date": None,
                    "is_current": True
                },
                {
                    "job_title": "Senior Software Developer",
                    "company": "Munich Cloud Solutions",
                    "start_date": "2017-04",
                    "end_date": "2020-12",
                    "is_current": None
                }
            ],
            "education": [
                {
                    "degree": "PhD in Computer Science",
                    "institution": "Technical University of Munich",
                    "graduation_year": 2017
                }
            ],
            "raw_text": text22
        }
    }
    with open(GROUND_TRUTH_DIR / "intl_germany_berlin.json", "w", encoding="utf-8") as f:
        json.dump(gt22, f, indent=2)

    # ==========================================
    # 23. intl_japan_tokyo.pdf (International PDF)
    # ==========================================
    doc23 = fitz.open()
    page23 = doc23.new_page()
    text23 = (
        "Kenji Tanaka\n"
        "kenji.tanaka@tokyo-lab.jp | +81 3 1234 5678 | Tokyo, Japan\n\n"
        "Professional Summary\n"
        "Full Stack Engineer with extensive experience in cloud architecture and distributed microservices.\n\n"
        "Work Experience\n"
        "Senior Software Engineer, Rakuten Group\n"
        "April 2021 - Present\n"
        "- Built scalable web applications using TypeScript and React\n\n"
        "Software Engineer, Sony Corporation\n"
        "April 2018 - March 2021\n"
        "- Developed backend cloud services in Go and AWS\n\n"
        "Education\n"
        "Master of Science in Information Science, University of Tokyo, 2018\n\n"
        "Skills\n"
        "TypeScript, React, Node.js, Go, AWS, Docker, Kubernetes, PostgreSQL, Git\n\n"
        "Languages\n"
        "Japanese, English"
    )
    page23.insert_text((50, 60), text23, fontsize=10)
    doc23.save(str(RESUMES_DIR / "intl_japan_tokyo.pdf"))
    doc23.close()

    gt23 = {
        "resume_id": "intl_japan_tokyo",
        "source_file": "intl_japan_tokyo.pdf",
        "expected": {
            "personal_info": {
                "name": "Kenji Tanaka",
                "email": "kenji.tanaka@tokyo-lab.jp",
                "phone": "+81 3 1234 5678",
                "location": "Tokyo, Japan"
            },
            "professional_summary": "Full Stack Engineer with extensive experience in cloud architecture and distributed microservices.",
            "skills": ["TypeScript", "React", "Node.js", "Go", "AWS", "Docker", "Kubernetes", "PostgreSQL", "Git"],
            "languages": ["Japanese", "English"],
            "experience": [
                {
                    "job_title": "Senior Software Engineer",
                    "company": "Rakuten Group",
                    "start_date": "2021-04",
                    "end_date": None,
                    "is_current": True
                },
                {
                    "job_title": "Software Engineer",
                    "company": "Sony Corporation",
                    "start_date": "2018-04",
                    "end_date": "2021-03",
                    "is_current": None
                }
            ],
            "education": [
                {
                    "degree": "Master of Science in Information Science",
                    "institution": "University of Tokyo",
                    "graduation_year": 2018
                }
            ],
            "raw_text": text23
        }
    }
    with open(GROUND_TRUTH_DIR / "intl_japan_tokyo.json", "w", encoding="utf-8") as f:
        json.dump(gt23, f, indent=2)

    # ==========================================
    # 24. intl_uk_london.pdf (International PDF)
    # ==========================================
    doc24 = fitz.open()
    page24 = doc24.new_page()
    text24 = (
        "Fiona MacLeod\n"
        "fiona.macleod@londontech.co.uk | +44 20 7946 0958 | London, United Kingdom\n\n"
        "Professional Summary\n"
        "Lead Data Engineer building large-scale streaming pipelines and modern data platforms.\n\n"
        "Work Experience\n"
        "Lead Data Engineer, FinTech London\n"
        "February 2021 - Present\n"
        "- Built real-time Kafka streaming architectures\n\n"
        "Data Engineer, Thames Analytics\n"
        "September 2018 - January 2021\n"
        "- Managed Snowflake data warehouse and dbt transformations\n\n"
        "Education\n"
        "Master of Science in Computing, University of Cambridge, 2018\n\n"
        "Skills\n"
        "Python, SQL, Kafka, Snowflake, dbt, Spark, AWS, Docker, Git, Linux\n\n"
        "Languages\n"
        "English, French"
    )
    page24.insert_text((50, 60), text24, fontsize=10)
    doc24.save(str(RESUMES_DIR / "intl_uk_london.pdf"))
    doc24.close()

    gt24 = {
        "resume_id": "intl_uk_london",
        "source_file": "intl_uk_london.pdf",
        "expected": {
            "personal_info": {
                "name": "Fiona MacLeod",
                "email": "fiona.macleod@londontech.co.uk",
                "phone": "+44 20 7946 0958",
                "location": "London, United Kingdom"
            },
            "professional_summary": "Lead Data Engineer building large-scale streaming pipelines and modern data platforms.",
            "skills": ["Python", "SQL", "Kafka", "Snowflake", "dbt", "Spark", "AWS", "Docker", "Git", "Linux"],
            "languages": ["English", "French"],
            "experience": [
                {
                    "job_title": "Lead Data Engineer",
                    "company": "FinTech London",
                    "start_date": "2021-02",
                    "end_date": None,
                    "is_current": True
                },
                {
                    "job_title": "Data Engineer",
                    "company": "Thames Analytics",
                    "start_date": "2018-09",
                    "end_date": "2021-01",
                    "is_current": None
                }
            ],
            "education": [
                {
                    "degree": "Master of Science in Computing",
                    "institution": "University of Cambridge",
                    "graduation_year": 2018
                }
            ],
            "raw_text": text24
        }
    }
    with open(GROUND_TRUTH_DIR / "intl_uk_london.json", "w", encoding="utf-8") as f:
        json.dump(gt24, f, indent=2)

    # ==========================================
    # 25. intl_brazil_saopaulo.docx (International DOCX)
    # ==========================================
    doc25 = Document()
    doc25.add_heading("Rodrigo Silva", level=0)
    doc25.add_paragraph("rodrigo.silva@techpaulista.com.br | +55 11 98765 4321 | Sao Paulo, Brazil")
    doc25.add_heading("Professional Summary", level=1)
    doc25.add_paragraph("Backend Developer specializing in cloud-native microservices and distributed databases.")
    doc25.add_heading("Work Experience", level=1)
    doc25.add_paragraph("Senior Backend Developer, NuvemTech Solucoes\nMay 2021 - Present\n- Developed Java and Spring microservices\n- Deployed containerized applications to Kubernetes")
    doc25.add_paragraph("Backend Developer, Paulista Software\nJanuary 2019 - April 2021\n- Built REST APIs with Python and PostgreSQL")
    doc25.add_heading("Education", level=1)
    doc25.add_paragraph("Bachelor of Science in Computer Science, Universidade de Sao Paulo, 2018")
    doc25.add_heading("Skills", level=1)
    doc25.add_paragraph("Java, Spring, Python, Docker, Kubernetes, PostgreSQL, Redis, AWS, Git")
    doc25.add_heading("Languages", level=1)
    doc25.add_paragraph("Portuguese, English, Spanish")

    docx25_path = RESUMES_DIR / "intl_brazil_saopaulo.docx"
    doc25.save(str(docx25_path))

    gt25 = {
        "resume_id": "intl_brazil_saopaulo",
        "source_file": "intl_brazil_saopaulo.docx",
        "expected": {
            "personal_info": {
                "name": "Rodrigo Silva",
                "email": "rodrigo.silva@techpaulista.com.br",
                "phone": "+55 11 98765 4321",
                "location": "Sao Paulo, Brazil"
            },
            "professional_summary": "Backend Developer specializing in cloud-native microservices and distributed databases.",
            "skills": ["Java", "Spring", "Python", "Docker", "Kubernetes", "PostgreSQL", "Redis", "AWS", "Git"],
            "languages": ["Portuguese", "English", "Spanish"],
            "experience": [
                {
                    "job_title": "Senior Backend Developer",
                    "company": "NuvemTech Solucoes",
                    "start_date": "2021-05",
                    "end_date": None,
                    "is_current": True
                },
                {
                    "job_title": "Backend Developer",
                    "company": "Paulista Software",
                    "start_date": "2019-01",
                    "end_date": "2021-04",
                    "is_current": None
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "institution": "Universidade de Sao Paulo",
                    "graduation_year": 2018
                }
            ]
        }
    }
    with open(GROUND_TRUTH_DIR / "intl_brazil_saopaulo.json", "w", encoding="utf-8") as f:
        json.dump(gt25, f, indent=2)

    # ==========================================
    # Generate BIO files and splits.json
    # ==========================================
    from tools.bio_converter import convert_to_bio, save_bio_file
    from tests.evaluation.ground_truth import load_ground_truth
    from app.services.pipeline import parse_resume

    all_resume_ids = []
    for gt_path in sorted(GROUND_TRUTH_DIR.glob("*.json")):
        gt = load_ground_truth(gt_path)
        all_resume_ids.append(gt.resume_id)
        resume_file = RESUMES_DIR / gt.source_file
        ext = resume_file.suffix.lstrip(".")
        parsed = parse_resume(resume_file, ext)
        raw_text = parsed.raw_text or gt.expected.raw_text or ""
        bio_tokens = convert_to_bio(raw_text, gt)
        bio_file = BIO_DIR / f"{gt.resume_id}.bio"
        save_bio_file(bio_tokens, bio_file)

    splits = {
        "train": [
            "simple_single_column",
            "compact_no_blanks",
            "skills_heavy",
            "education_focused",
            "table_resume",
            "single_col_datascience",
            "single_col_devops",
            "twocol_software_eng",
            "twocol_product_mgr",
            "multipage_senior_architect",
            "docx_table_consultant",
            "docx_plain_sysadmin",
            "scanned_analyst",
            "intl_germany_berlin",
            "intl_japan_tokyo"
        ],
        "val": [
            "single_col_mobile",
            "twocol_data_analyst",
            "multipage_academic_researcher",
            "docx_plain_security_eng",
            "intl_uk_london"
        ],
        "test": [
            "twocol_cloud_architect",
            "multipage_engineering_manager",
            "docx_table_qa_lead",
            "scanned_developer",
            "intl_brazil_saopaulo"
        ]
    }
    with open(FIXTURES_DIR / "splits.json", "w", encoding="utf-8") as f:
        json.dump(splits, f, indent=2)

    print(f"Generated {len(all_resume_ids)} resumes, ground truths, and BIO files.")
    print(f"Splits: {len(splits['train'])} train, {len(splits['val'])} val, {len(splits['test'])} test.")

if __name__ == "__main__":
    generate_fixtures()
