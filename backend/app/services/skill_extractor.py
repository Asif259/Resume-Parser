import re
from app.schemas.evidence import FieldEvidence

# Canonical skill name -> list of aliases (all lowercase)
SKILL_DICTIONARY: dict[str, list[str]] = {
    # Programming Languages
    "Python": ["python", "python3"],
    "JavaScript": ["javascript", "js", "ecmascript"],
    "TypeScript": ["typescript", "ts"],
    "Java": ["java"],
    "C++": ["c++", "cpp"],
    "C#": ["c#", "csharp", "c sharp"],
    "C": [],  # handled specially due to single-letter risk
    "Go": ["golang"],
    "Rust": ["rust"],
    "Ruby": ["ruby"],
    "PHP": ["php"],
    "Swift": ["swift"],
    "Kotlin": ["kotlin"],
    "Scala": ["scala"],
    "R": [],  # handled specially
    "Dart": ["dart"],
    "Lua": ["lua"],
    "Perl": ["perl"],
    "Haskell": ["haskell"],
    "Elixir": ["elixir"],
    "Clojure": ["clojure"],
    "Shell": ["shell", "bash", "zsh", "shell scripting"],
    "SQL": ["sql"],
    "GraphQL": ["graphql", "gql"],
    "Solidity": ["solidity"],

    # Frontend
    "React": ["react", "reactjs", "react.js", "react js"],
    "Angular": ["angular", "angularjs", "angular.js"],
    "Vue.js": ["vue", "vuejs", "vue.js", "vue js"],
    "Svelte": ["svelte", "sveltekit"],
    "Next.js": ["next", "nextjs", "next.js", "next js"],
    "Nuxt.js": ["nuxt", "nuxtjs", "nuxt.js"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "SASS": ["sass", "scss"],
    "Tailwind CSS": ["tailwind", "tailwindcss", "tailwind css"],
    "Bootstrap": ["bootstrap"],
    "jQuery": ["jquery"],
    "Redux": ["redux"],
    "Webpack": ["webpack"],
    "Vite": ["vite"],

    # Backend
    "Node.js": ["node", "nodejs", "node.js", "node js"],
    "Express": ["express", "expressjs", "express.js"],
    "Django": ["django"],
    "Flask": ["flask"],
    "FastAPI": ["fastapi", "fast api"],
    "Spring Boot": ["spring boot", "spring", "springboot"],
    "Ruby on Rails": ["rails", "ruby on rails", "ror"],
    "Laravel": ["laravel"],
    "ASP.NET": ["asp.net", "aspnet", "asp net", ".net", "dotnet"],
    "NestJS": ["nestjs", "nest.js", "nest js"],

    # Databases
    "PostgreSQL": ["postgresql", "postgres", "psql", "pg"],
    "MySQL": ["mysql"],
    "MongoDB": ["mongodb", "mongo"],
    "Redis": ["redis"],
    "SQLite": ["sqlite", "sqlite3"],
    "Cassandra": ["cassandra"],
    "Elasticsearch": ["elasticsearch", "elastic search", "elastic"],
    "DynamoDB": ["dynamodb", "dynamo"],
    "Firebase": ["firebase", "firestore"],
    "MariaDB": ["mariadb"],
    "Oracle DB": ["oracle", "oracle db", "oracledb"],
    "SQL Server": ["sql server", "mssql", "microsoft sql server"],
    "Neo4j": ["neo4j"],

    # DevOps & Cloud
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure", "microsoft azure"],
    "GCP": ["gcp", "google cloud", "google cloud platform"],
    "Terraform": ["terraform"],
    "Ansible": ["ansible"],
    "Pulumi": ["pulumi"],
    "CloudFormation": ["cloudformation"],
    "Chef": ["chef"],
    "Puppet": ["puppet"],
    "Jenkins": ["jenkins"],
    "CircleCI": ["circleci", "circle ci"],
    "GitHub Actions": ["github actions"],
    "GitLab CI": ["gitlab ci", "gitlab ci/cd"],
    "Nginx": ["nginx"],
    "Apache": ["apache"],
    "Vercel": ["vercel"],
    "Heroku": ["heroku"],
    "Netlify": ["netlify"],
    "Linux": ["linux", "ubuntu", "centos", "debian"],

    # Data Engineering
    "Spark": ["spark", "apache spark"],
    "Airflow": ["airflow", "apache airflow"],
    "dbt": ["dbt"],
    "Flink": ["flink", "apache flink"],
    "Snowflake": ["snowflake"],
    "BigQuery": ["bigquery", "big query"],
    "Redshift": ["redshift"],
    "Databricks": ["databricks"],
    "Fivetran": ["fivetran"],
    "Hadoop": ["hadoop"],

    # Observability & Monitoring
    "Prometheus": ["prometheus"],
    "Grafana": ["grafana"],
    "Datadog": ["datadog"],
    "New Relic": ["new relic", "newrelic"],
    "Splunk": ["splunk"],
    "ELK": ["elk", "elk stack", "logstash", "kibana"],
    "OpenTelemetry": ["opentelemetry", "otel"],
    "Jaeger": ["jaeger"],

    # Security
    "OWASP": ["owasp"],
    "Vault": ["vault", "hashicorp vault"],
    "SAML": ["saml"],

    # Modern Frameworks
    "Remix": ["remix"],
    "Astro": ["astro"],
    "SolidJS": ["solid", "solidjs", "solid.js"],
    "htmx": ["htmx"],
    "Turbo": ["turbo", "turbopack", "turborepo"],
    "Stimulus": ["stimulus"],

    # Tools
    "Git": ["git"],
    "GitHub": ["github"],
    "GitLab": ["gitlab"],
    "Bitbucket": ["bitbucket"],
    "Jira": ["jira"],
    "Confluence": ["confluence"],
    "Figma": ["figma"],
    "VS Code": ["vscode", "vs code", "visual studio code"],
    "Postman": ["postman"],
    "Swagger": ["swagger", "openapi"],

    # Testing
    "Jest": ["jest"],
    "Pytest": ["pytest"],
    "Mocha": ["mocha"],
    "Cypress": ["cypress"],
    "Selenium": ["selenium"],
    "JUnit": ["junit"],
    "RSpec": ["rspec"],

    # Data Science / AI / ML
    "TensorFlow": ["tensorflow", "tf"],
    "PyTorch": ["pytorch"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "Keras": ["keras"],
    "OpenCV": ["opencv"],
    "Matplotlib": ["matplotlib"],
    "Jupyter": ["jupyter", "jupyter notebook"],
    "Hugging Face": ["hugging face", "huggingface"],
    "LangChain": ["langchain"],
    "spaCy": ["spacy"],

    # Mobile
    "React Native": ["react native"],
    "Flutter": ["flutter"],
    "SwiftUI": ["swiftui"],
    "Jetpack Compose": ["jetpack compose"],
    "Android": ["android"],
    "iOS": ["ios"],

    # Messaging / Streaming
    "Kafka": ["kafka", "apache kafka"],
    "RabbitMQ": ["rabbitmq"],

    # Other
    "REST API": ["rest", "rest api", "restful", "restful api"],
    "gRPC": ["grpc"],
    "WebSocket": ["websocket", "websockets"],
    "OAuth": ["oauth", "oauth2", "oauth 2.0"],
    "JWT": ["jwt", "json web token"],
    "Agile": ["agile", "scrum"],
    "CI/CD": ["ci/cd", "cicd", "continuous integration"],
    "Microservices": ["microservices", "micro services"],
}

# Build reverse lookup: lowercase alias -> canonical name
_ALIAS_TO_CANONICAL: dict[str, str] = {}
for canonical, aliases in SKILL_DICTIONARY.items():
    _ALIAS_TO_CANONICAL[canonical.lower()] = canonical
    for alias in aliases:
        _ALIAS_TO_CANONICAL[alias.lower()] = canonical

# Skills that need word boundary matching to avoid false positives
_SHORT_SKILLS = {"go", "r", "c", "c#", "c++", "rust", "dart", "lua", "perl", "rest", "jwt", "git", "dbt"}


def _match_skill_in_text(text_lower: str, alias: str) -> bool:
    """Check if alias appears in text with word boundaries."""
    # Escape regex special chars in alias
    escaped = re.escape(alias)
    pattern = rf'(?<![a-zA-Z0-9_/.]){escaped}(?![a-zA-Z0-9_/.])'
    return bool(re.search(pattern, text_lower))


def extract_skills_with_evidence(sections: dict[str, str]) -> tuple[list[str], dict[str, FieldEvidence]]:
    """Extract and normalize skills from resume sections, preserving field evidence."""
    found: set[str] = set()
    evidence: dict[str, FieldEvidence] = {}

    skills_text = sections.get("skills", "")

    # 1. Parse skills section: split by comma, pipe, semicolon, bullet, newline
    if skills_text:
        tokens = re.split(r'[,|;•●○▪\n]+', skills_text)
        for token in tokens:
            token_clean = token.strip().lower()
            if not token_clean:
                continue
            canonical = _ALIAS_TO_CANONICAL.get(token_clean)
            if canonical:
                found.add(canonical)
                if canonical not in evidence:
                    evidence[canonical] = FieldEvidence(
                        value=token.strip(),
                        normalized_value=canonical,
                        source_section="skills",
                        source_text=token.strip(),
                        confidence=0.95,
                    )
                continue
            for alias, canon in _ALIAS_TO_CANONICAL.items():
                if alias in token_clean and _match_skill_in_text(token_clean, alias):
                    found.add(canon)
                    if canon not in evidence:
                        evidence[canon] = FieldEvidence(
                            value=alias,
                            normalized_value=canon,
                            source_section="skills",
                            source_text=token.strip(),
                            confidence=0.90,
                        )

    # 2. Scan other sections for skill mentions
    scan_sections = ["experience", "summary", "projects", "education", "other"]
    for sec_name in scan_sections:
        sec_text = sections.get(sec_name, "")
        if not sec_text.strip():
            continue
        sec_lower = sec_text.lower()
        for alias, canonical in _ALIAS_TO_CANONICAL.items():
            if canonical in found:
                continue
            if len(alias) <= 2 and alias in _SHORT_SKILLS:
                if _match_skill_in_text(sec_lower, alias):
                    if alias == "go":
                        continue
                    found.add(canonical)
                    evidence[canonical] = FieldEvidence(
                        value=alias,
                        normalized_value=canonical,
                        source_section=sec_name,
                        source_text=alias,
                        confidence=0.75,
                    )
            elif alias in sec_lower:
                if _match_skill_in_text(sec_lower, alias):
                    found.add(canonical)
                    evidence[canonical] = FieldEvidence(
                        value=alias,
                        normalized_value=canonical,
                        source_section=sec_name,
                        source_text=alias,
                        confidence=0.75,
                    )

    return sorted(found), evidence


def extract_skills(sections: dict[str, str]) -> list[str]:
    """Extract and normalize skills from resume sections."""
    skills, _ = extract_skills_with_evidence(sections)
    return skills

