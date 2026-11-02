from typing import Any

# Comprehensive skill taxonomy: canonical skill name -> category, aliases, description
SKILL_TAXONOMY: dict[str, dict[str, Any]] = {
    # Programming Languages
    "Python": {
        "category": "programming_languages",
        "aliases": ["python", "python3", "cpython"],
        "description": "Python programming language, scripting, backend and data science",
    },
    "JavaScript": {
        "category": "programming_languages",
        "aliases": ["javascript", "js", "ecmascript"],
        "description": "JavaScript web development programming language",
    },
    "TypeScript": {
        "category": "programming_languages",
        "aliases": ["typescript", "ts"],
        "description": "TypeScript typed superset of JavaScript",
    },
    "Java": {
        "category": "programming_languages",
        "aliases": ["java", "jvm"],
        "description": "Java enterprise programming language",
    },
    "C++": {
        "category": "programming_languages",
        "aliases": ["c++", "cpp"],
        "description": "C++ systems programming language",
    },
    "C#": {
        "category": "programming_languages",
        "aliases": ["c#", "csharp", "c sharp"],
        "description": "C# Microsoft .NET programming language",
    },
    "C": {
        "category": "programming_languages",
        "aliases": ["c language"],
        "description": "C low-level systems programming language",
    },
    "Go": {
        "category": "programming_languages",
        "aliases": ["go", "golang"],
        "description": "Go programming language by Google for microservices",
    },
    "Rust": {
        "category": "programming_languages",
        "aliases": ["rust"],
        "description": "Rust memory-safe systems programming language",
    },
    "Ruby": {
        "category": "programming_languages",
        "aliases": ["ruby"],
        "description": "Ruby dynamic object-oriented programming language",
    },
    "PHP": {
        "category": "programming_languages",
        "aliases": ["php"],
        "description": "PHP server-side scripting language",
    },
    "Swift": {
        "category": "programming_languages",
        "aliases": ["swift"],
        "description": "Swift programming language for Apple iOS and macOS",
    },
    "Kotlin": {
        "category": "programming_languages",
        "aliases": ["kotlin"],
        "description": "Kotlin programming language for Android and backend",
    },
    "Scala": {
        "category": "programming_languages",
        "aliases": ["scala"],
        "description": "Scala functional programming language on JVM",
    },
    "R": {
        "category": "programming_languages",
        "aliases": ["r language"],
        "description": "R statistical computing and graphics language",
    },
    "Dart": {
        "category": "programming_languages",
        "aliases": ["dart"],
        "description": "Dart client-optimized programming language for Flutter",
    },
    "Lua": {
        "category": "programming_languages",
        "aliases": ["lua"],
        "description": "Lua lightweight embedded scripting language",
    },
    "Perl": {
        "category": "programming_languages",
        "aliases": ["perl"],
        "description": "Perl text processing and scripting language",
    },
    "SQL": {
        "category": "programming_languages",
        "aliases": ["sql", "structured query language"],
        "description": "SQL relational database query language",
    },
    "GraphQL": {
        "category": "programming_languages",
        "aliases": ["graphql", "gql"],
        "description": "GraphQL API query language and runtime",
    },
    "Shell": {
        "category": "programming_languages",
        "aliases": ["shell", "bash", "zsh", "shell scripting"],
        "description": "Unix shell scripting and command line",
    },

    # Frontend
    "React": {
        "category": "frontend",
        "aliases": ["react", "reactjs", "react.js", "react js"],
        "description": "React JavaScript frontend UI library",
    },
    "Angular": {
        "category": "frontend",
        "aliases": ["angular", "angularjs", "angular.js"],
        "description": "Angular TypeScript frontend web framework",
    },
    "Vue.js": {
        "category": "frontend",
        "aliases": ["vue", "vuejs", "vue.js", "vue js"],
        "description": "Vue.js progressive frontend JavaScript framework",
    },
    "Svelte": {
        "category": "frontend",
        "aliases": ["svelte", "sveltekit"],
        "description": "Svelte component framework compiler",
    },
    "Next.js": {
        "category": "frontend",
        "aliases": ["next", "nextjs", "next.js", "next js"],
        "description": "Next.js React full-stack web framework with SSR",
    },
    "HTML": {
        "category": "frontend",
        "aliases": ["html", "html5"],
        "description": "HyperText Markup Language standard for web pages",
    },
    "CSS": {
        "category": "frontend",
        "aliases": ["css", "css3"],
        "description": "Cascading Style Sheets for web styling",
    },
    "Tailwind CSS": {
        "category": "frontend",
        "aliases": ["tailwind", "tailwindcss", "tailwind css"],
        "description": "Tailwind CSS utility-first CSS styling framework",
    },
    "Redux": {
        "category": "frontend",
        "aliases": ["redux", "redux toolkit"],
        "description": "Redux state management for JavaScript apps",
    },

    # Backend
    "Node.js": {
        "category": "backend",
        "aliases": ["node", "nodejs", "node.js", "node js"],
        "description": "Node.js JavaScript server runtime environment",
    },
    "Express": {
        "category": "backend",
        "aliases": ["express", "expressjs", "express.js"],
        "description": "Express.js web application framework for Node",
    },
    "Django": {
        "category": "backend",
        "aliases": ["django"],
        "description": "Django high-level Python web framework",
    },
    "Flask": {
        "category": "backend",
        "aliases": ["flask"],
        "description": "Flask lightweight Python microframework",
    },
    "FastAPI": {
        "category": "backend",
        "aliases": ["fastapi", "fast api"],
        "description": "FastAPI modern high-performance Python API framework",
    },
    "Spring Boot": {
        "category": "backend",
        "aliases": ["spring boot", "spring", "springboot"],
        "description": "Spring Boot enterprise Java framework",
    },
    "Ruby on Rails": {
        "category": "backend",
        "aliases": ["rails", "ruby on rails", "ror"],
        "description": "Ruby on Rails web application framework",
    },
    "ASP.NET": {
        "category": "backend",
        "aliases": ["asp.net", "aspnet", "asp net", ".net", "dotnet"],
        "description": "ASP.NET Microsoft web application framework",
    },

    # Databases
    "PostgreSQL": {
        "category": "databases",
        "aliases": ["postgresql", "postgres", "psql", "pg"],
        "description": "PostgreSQL open-source relational database management system",
    },
    "MySQL": {
        "category": "databases",
        "aliases": ["mysql"],
        "description": "MySQL relational database management system",
    },
    "MongoDB": {
        "category": "databases",
        "aliases": ["mongodb", "mongo"],
        "description": "MongoDB document-based NoSQL database",
    },
    "Redis": {
        "category": "databases",
        "aliases": ["redis"],
        "description": "Redis in-memory data store, cache and message broker",
    },
    "Elasticsearch": {
        "category": "databases",
        "aliases": ["elasticsearch", "elastic search", "elastic"],
        "description": "Elasticsearch distributed search and analytics engine",
    },
    "Firebase": {
        "category": "databases",
        "aliases": ["firebase", "firestore"],
        "description": "Google Firebase real-time database and backend platform",
    },

    # DevOps & Cloud
    "Docker": {
        "category": "devops_cloud",
        "aliases": ["docker", "containerization"],
        "description": "Docker container platform for deploying applications",
    },
    "Kubernetes": {
        "category": "devops_cloud",
        "aliases": ["kubernetes", "k8s"],
        "description": "Kubernetes container orchestration system",
    },
    "AWS": {
        "category": "devops_cloud",
        "aliases": ["aws", "amazon web services"],
        "description": "Amazon Web Services cloud computing platform",
    },
    "Azure": {
        "category": "devops_cloud",
        "aliases": ["azure", "microsoft azure"],
        "description": "Microsoft Azure cloud computing services",
    },
    "GCP": {
        "category": "devops_cloud",
        "aliases": ["gcp", "google cloud", "google cloud platform"],
        "description": "Google Cloud Platform cloud infrastructure",
    },
    "Terraform": {
        "category": "devops_cloud",
        "aliases": ["terraform", "iac"],
        "description": "Terraform infrastructure as code provisioning tool",
    },
    "Ansible": {
        "category": "devops_cloud",
        "aliases": ["ansible"],
        "description": "Ansible IT automation and configuration management tool",
    },
    "Jenkins": {
        "category": "devops_cloud",
        "aliases": ["jenkins"],
        "description": "Jenkins open-source CI/CD automation server",
    },
    "Linux": {
        "category": "devops_cloud",
        "aliases": ["linux", "ubuntu", "centos", "debian"],
        "description": "Linux operating system and system administration",
    },

    # Data Engineering
    "Spark": {
        "category": "data_engineering",
        "aliases": ["spark", "apache spark"],
        "description": "Apache Spark unified engine for big data processing",
    },
    "Airflow": {
        "category": "data_engineering",
        "aliases": ["airflow", "apache airflow"],
        "description": "Apache Airflow workflow orchestration platform",
    },
    "dbt": {
        "category": "data_engineering",
        "aliases": ["dbt", "data build tool"],
        "description": "dbt analytics engineering and data transformation tool",
    },
    "Snowflake": {
        "category": "data_engineering",
        "aliases": ["snowflake"],
        "description": "Snowflake cloud data warehouse and analytics platform",
    },
    "Kafka": {
        "category": "data_engineering",
        "aliases": ["kafka", "apache kafka"],
        "description": "Apache Kafka distributed event streaming platform",
    },

    # Observability
    "Prometheus": {
        "category": "observability",
        "aliases": ["prometheus"],
        "description": "Prometheus systems monitoring and alerting toolkit",
    },
    "Grafana": {
        "category": "observability",
        "aliases": ["grafana"],
        "description": "Grafana operational analytics and visualization dashboard",
    },
    "Splunk": {
        "category": "observability",
        "aliases": ["splunk"],
        "description": "Splunk machine data analytics and SIEM monitoring platform",
    },

    # AI & ML
    "TensorFlow": {
        "category": "ai_ml",
        "aliases": ["tensorflow", "tf"],
        "description": "TensorFlow open-source machine learning framework",
    },
    "PyTorch": {
        "category": "ai_ml",
        "aliases": ["pytorch"],
        "description": "PyTorch deep learning framework",
    },
    "Pandas": {
        "category": "ai_ml",
        "aliases": ["pandas"],
        "description": "Pandas data analysis and manipulation library",
    },
    "NumPy": {
        "category": "ai_ml",
        "aliases": ["numpy"],
        "description": "NumPy numerical mathematics array library",
    },
    "Scikit-learn": {
        "category": "ai_ml",
        "aliases": ["scikit-learn", "sklearn", "scikit learn"],
        "description": "Scikit-learn machine learning in Python",
    },

    # Testing & Tools
    "Git": {
        "category": "tools",
        "aliases": ["git", "version control"],
        "description": "Git distributed version control system",
    },
    "Jira": {
        "category": "tools",
        "aliases": ["jira"],
        "description": "Jira issue tracking and agile project management",
    },
    "Figma": {
        "category": "tools",
        "aliases": ["figma"],
        "description": "Figma collaborative web UI/UX design tool",
    },
    "Selenium": {
        "category": "testing",
        "aliases": ["selenium"],
        "description": "Selenium browser automation testing framework",
    },
    "Cypress": {
        "category": "testing",
        "aliases": ["cypress"],
        "description": "Cypress modern end-to-end web testing tool",
    },
    "Playwright": {
        "category": "testing",
        "aliases": ["playwright"],
        "description": "Playwright cross-browser end-to-end test automation",
    },
    "Jest": {
        "category": "testing",
        "aliases": ["jest"],
        "description": "Jest JavaScript testing framework",
    },

    # Mobile & Concepts
    "React Native": {
        "category": "mobile",
        "aliases": ["react native"],
        "description": "React Native framework for building native iOS and Android apps",
    },
    "Flutter": {
        "category": "mobile",
        "aliases": ["flutter"],
        "description": "Flutter Google UI toolkit for building natively compiled apps",
    },
    "iOS": {
        "category": "mobile",
        "aliases": ["ios", "apple mobile"],
        "description": "iOS Apple mobile operating system development",
    },
    "Android": {
        "category": "mobile",
        "aliases": ["android"],
        "description": "Android Google mobile operating system development",
    },
    "Agile": {
        "category": "methodology",
        "aliases": ["agile", "scrum", "kanban"],
        "description": "Agile software development methodology and Scrum framework",
    },
    "CI/CD": {
        "category": "devops_cloud",
        "aliases": ["ci/cd", "cicd", "continuous integration", "continuous deployment"],
        "description": "CI/CD continuous integration and continuous delivery pipeline",
    },
    "Microservices": {
        "category": "architecture",
        "aliases": ["microservices", "micro services", "service oriented"],
        "description": "Microservices distributed architectural design pattern",
    },
    "REST": {
        "category": "architecture",
        "aliases": ["rest", "rest api", "restful", "restful api"],
        "description": "REST Representational State Transfer web API architecture",
    },
}

