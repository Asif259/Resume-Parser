import re

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
_SHORT_SKILLS = {"go", "r", "c", "c#", "c++", "rust", "dart", "lua", "perl", "rest", "jwt", "git"}


def _match_skill_in_text(text_lower: str, alias: str) -> bool:
    """Check if alias appears in text with word boundaries."""
    # Escape regex special chars in alias
    escaped = re.escape(alias)
    pattern = rf'(?<![a-zA-Z0-9_/.]){escaped}(?![a-zA-Z0-9_/.])'
    return bool(re.search(pattern, text_lower))


def extract_skills(sections: dict[str, str]) -> list[str]:
    """Extract and normalize skills from resume sections.

    1. Parse skills section by comma/pipe/newline delimiters and match against dictionary.
    2. Scan other sections for skill mentions using word-boundary matching.
    3. Deduplicate and sort.
    """
    found: set[str] = set()

    skills_text = sections.get("skills", "")

    # 1. Parse skills section: split by comma, pipe, semicolon, bullet, newline
    if skills_text:
        tokens = re.split(r'[,|;•●○▪\n]+', skills_text)
        for token in tokens:
            token_clean = token.strip().lower()
            if not token_clean:
                continue
            # Direct lookup
            canonical = _ALIAS_TO_CANONICAL.get(token_clean)
            if canonical:
                found.add(canonical)
                continue
            # Try substring match within the token for multi-word skills
            for alias, canon in _ALIAS_TO_CANONICAL.items():
                if alias in token_clean and _match_skill_in_text(token_clean, alias):
                    found.add(canon)

    # 2. Scan other sections for skill mentions
    scan_sections = ["experience", "summary", "projects", "education", "other"]
    scan_text = " ".join(sections.get(k, "") for k in scan_sections).lower()

    if scan_text.strip():
        for alias, canonical in _ALIAS_TO_CANONICAL.items():
            if canonical in found:
                continue
            if len(alias) <= 2 and alias in _SHORT_SKILLS:
                # Extra strict for very short aliases: require exact word boundary
                if _match_skill_in_text(scan_text, alias):
                    # Additional check: "go" must not be just the verb
                    if alias == "go":
                        # Only match "Go" or "Golang", not "go to" "go ahead"
                        continue  # Skip "go" from non-skills sections
                    found.add(canonical)
            elif alias in scan_text:
                if _match_skill_in_text(scan_text, alias):
                    found.add(canonical)

    return sorted(found)
