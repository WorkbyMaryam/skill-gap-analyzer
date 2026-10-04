"""Curated skill ontology.

Each skill: canonical name -> category + aliases (surface forms found in text).
Edit this file to extend the analyzer to new domains; no other code changes needed.
"""
from __future__ import annotations

# (canonical, category, [aliases])
_RAW_SKILLS = [
    # ---- Programming languages
    ("Python", "Programming", ["python", "python3"]),
    ("R", "Programming", ["r programming", "r language", "rstudio", "r studio", "tidyverse", "ggplot2", "ggplot"]),
    ("Java", "Programming", ["java", "core java"]),
    ("JavaScript", "Programming", ["javascript", "js", "ecmascript", "es6"]),
    ("TypeScript", "Programming", ["typescript"]),
    ("C++", "Programming", ["c++", "cpp"]),
    ("C#", "Programming", ["c#", "csharp"]),
    (".NET", "Programming", [".net", "dotnet", "asp.net"]),
    ("Go", "Programming", ["golang", "go lang", "go programming"]),
    ("Scala", "Programming", ["scala"]),
    ("Rust", "Programming", ["rust"]),
    ("Bash/Shell", "Programming", ["bash", "shell scripting", "shell script", "unix shell"]),
    ("MATLAB", "Programming", ["matlab"]),
    ("SAS", "Programming", ["sas"]),
    ("PHP", "Programming", ["php"]),
    ("Kotlin", "Programming", ["kotlin"]),
    ("Swift", "Programming", ["swift"]),
    # ---- Databases
    ("SQL", "Databases", ["sql", "t-sql", "tsql", "pl/sql", "plsql", "structured query language"]),
    ("MySQL", "Databases", ["mysql", "mariadb"]),
    ("PostgreSQL", "Databases", ["postgresql", "postgres"]),
    ("SQL Server", "Databases", ["sql server", "mssql", "ms sql"]),
    ("Oracle DB", "Databases", ["oracle db", "oracle database", "oracle sql"]),
    ("SQLite", "Databases", ["sqlite"]),
    ("MongoDB", "Databases", ["mongodb", "mongo db"]),
    ("NoSQL", "Databases", ["nosql", "no-sql"]),
    ("Redis", "Databases", ["redis"]),
    ("Elasticsearch", "Databases", ["elasticsearch", "elastic search", "opensearch"]),
    ("Cassandra", "Databases", ["cassandra"]),
    ("Neo4j", "Databases", ["neo4j", "graph database"]),
    # ---- Data analysis & libraries
    ("Pandas", "Data Analysis", ["pandas"]),
    ("NumPy", "Data Analysis", ["numpy"]),
    ("SciPy", "Data Analysis", ["scipy"]),
    ("Statistics", "Data Analysis", ["statistics", "statistical analysis", "statistical modeling", "statistical modelling", "statistical", "hypothesis testing", "probability", "regression analysis"]),
    ("A/B Testing", "Data Analysis", ["a/b testing", "ab testing", "a/b test", "experimentation", "experiment design"]),
    ("Excel", "Data Analysis", ["excel", "ms excel", "microsoft excel", "spreadsheets", "google sheets"]),
    ("Advanced Excel", "Data Analysis", ["advanced excel", "pivot table", "pivot tables", "vlookup", "xlookup", "power query", "excel macros", "vba", "excel formulas", "index match"]),
    ("Data Cleaning", "Data Analysis", ["data cleaning", "data wrangling", "data preprocessing", "data preparation", "data munging", "data cleansing"]),
    ("Exploratory Data Analysis", "Data Analysis", ["eda", "exploratory data analysis", "exploratory analysis"]),
    ("Data Analysis", "Data Analysis", ["data analysis", "data analytics", "analytical skills"]),
    ("Time Series", "Data Analysis", ["time series", "time-series", "forecasting", "arima", "prophet"]),
    ("Feature Engineering", "Data Analysis", ["feature engineering", "feature selection"]),
    # ---- Visualization / BI
    ("Power BI", "Visualization & BI", ["power bi", "powerbi", "dax"]),
    ("Tableau", "Visualization & BI", ["tableau"]),
    ("Looker", "Visualization & BI", ["looker", "looker studio", "data studio"]),
    ("Qlik", "Visualization & BI", ["qlik", "qlikview", "qlik sense"]),
    ("Matplotlib", "Visualization & BI", ["matplotlib"]),
    ("Seaborn", "Visualization & BI", ["seaborn"]),
    ("Plotly", "Visualization & BI", ["plotly"]),
    ("Data Visualization", "Visualization & BI", ["data visualization", "data visualisation", "dashboards", "dashboarding", "dashboard"]),
    ("Business Intelligence", "Visualization & BI", ["business intelligence", "bi tools", "bi reporting"]),
    ("Streamlit", "Visualization & BI", ["streamlit"]),
    # ---- Machine learning
    ("Machine Learning", "Machine Learning", ["machine learning", "ml models", "predictive modeling", "predictive modelling", "predictive analytics", "supervised learning", "unsupervised learning"]),
    ("Scikit-learn", "Machine Learning", ["scikit-learn", "scikit learn", "sklearn"]),
    ("Deep Learning", "Machine Learning", ["deep learning", "neural network", "neural networks", "cnn", "rnn", "lstm"]),
    ("TensorFlow", "Machine Learning", ["tensorflow"]),
    ("PyTorch", "Machine Learning", ["pytorch", "torch"]),
    ("Keras", "Machine Learning", ["keras"]),
    ("XGBoost", "Machine Learning", ["xgboost", "lightgbm", "catboost", "gradient boosting"]),
    ("NLP", "Machine Learning", ["nlp", "natural language processing", "text mining", "text analytics", "spacy", "nltk"]),
    ("Computer Vision", "Machine Learning", ["computer vision", "opencv", "image classification", "object detection"]),
    ("LLMs", "Machine Learning", ["llm", "llms", "large language model", "large language models", "generative ai", "gen ai", "genai", "prompt engineering", "rag", "langchain"]),
    ("Hugging Face", "Machine Learning", ["hugging face", "huggingface", "transformers"]),
    ("Recommender Systems", "Machine Learning", ["recommender system", "recommender systems", "recommendation engine", "recommendation systems"]),
    ("Model Deployment", "Machine Learning", ["model deployment", "model serving", "deploying models", "mlops", "ml ops"]),
    ("MLflow", "Machine Learning", ["mlflow", "experiment tracking"]),
    ("Reinforcement Learning", "Machine Learning", ["reinforcement learning"]),
    # ---- Data engineering / big data
    ("ETL", "Data Engineering", ["etl", "elt", "data pipelines", "data pipeline", "data integration"]),
    ("Apache Spark", "Data Engineering", ["spark", "pyspark", "apache spark"]),
    ("Hadoop", "Data Engineering", ["hadoop", "hdfs", "mapreduce", "hive"]),
    ("Kafka", "Data Engineering", ["kafka", "apache kafka"]),
    ("Airflow", "Data Engineering", ["airflow", "apache airflow", "dagster", "prefect"]),
    ("dbt", "Data Engineering", ["dbt"]),
    ("Data Warehousing", "Data Engineering", ["data warehouse", "data warehousing", "data warehouses", "star schema", "dimensional modeling", "dimensional modelling"]),
    ("Snowflake", "Data Engineering", ["snowflake"]),
    ("Databricks", "Data Engineering", ["databricks"]),
    ("BigQuery", "Data Engineering", ["bigquery", "big query"]),
    ("Redshift", "Data Engineering", ["redshift"]),
    ("Big Data", "Data Engineering", ["big data"]),
    # ---- Cloud & DevOps
    ("AWS", "Cloud & DevOps", ["aws", "amazon web services", "s3", "ec2", "sagemaker", "lambda"]),
    ("Azure", "Cloud & DevOps", ["azure", "microsoft azure", "azure ml", "synapse"]),
    ("GCP", "Cloud & DevOps", ["gcp", "google cloud", "google cloud platform", "vertex ai"]),
    ("Docker", "Cloud & DevOps", ["docker", "containerization", "containers"]),
    ("Kubernetes", "Cloud & DevOps", ["kubernetes", "k8s"]),
    ("CI/CD", "Cloud & DevOps", ["ci/cd", "cicd", "continuous integration", "continuous delivery", "jenkins", "github actions", "gitlab ci"]),
    ("Git", "Cloud & DevOps", ["git", "github", "gitlab", "bitbucket", "version control"]),
    ("Terraform", "Cloud & DevOps", ["terraform", "infrastructure as code"]),
    ("Linux", "Cloud & DevOps", ["linux", "unix", "ubuntu"]),
    # ---- Software engineering
    ("REST APIs", "Software Engineering", ["rest api", "rest apis", "restful", "api development", "apis"]),
    ("FastAPI", "Software Engineering", ["fastapi"]),
    ("Flask", "Software Engineering", ["flask"]),
    ("Django", "Software Engineering", ["django"]),
    ("React", "Software Engineering", ["react", "reactjs", "react.js"]),
    ("Node.js", "Software Engineering", ["node.js", "nodejs", "node js", "express.js"]),
    ("HTML/CSS", "Software Engineering", ["html", "css", "html5", "css3"]),
    ("Microservices", "Software Engineering", ["microservices", "microservice"]),
    ("Unit Testing", "Software Engineering", ["unit testing", "pytest", "unit tests", "test automation", "tdd"]),
    ("Data Structures & Algorithms", "Software Engineering", ["data structures", "algorithms", "dsa"]),
    ("OOP", "Software Engineering", ["oop", "object-oriented", "object oriented"]),
    # ---- Methodology / business
    ("Agile/Scrum", "Methodology", ["agile", "scrum", "kanban", "sprint planning"]),
    ("Jira", "Methodology", ["jira", "confluence"]),
    ("Project Management", "Methodology", ["project management", "project manager", "pmp"]),
    ("Stakeholder Management", "Business", ["stakeholder management", "stakeholder communication", "stakeholders", "stakeholder"]),
    ("Business Analysis", "Business", ["business analysis", "business analyst", "requirements gathering", "requirement gathering"]),
    ("KPI & Metrics", "Business", ["kpi", "kpis", "metrics", "key performance indicators"]),
    ("Reporting", "Business", ["reporting", "ad hoc reporting", "ad-hoc reporting", "report generation"]),
    ("Data Storytelling", "Business", ["data storytelling", "storytelling with data", "insight communication", "presenting insights"]),
    ("Data Governance", "Business", ["data governance", "data quality", "data privacy", "gdpr", "data security"]),
    ("Product Analytics", "Business", ["product analytics", "google analytics", "mixpanel", "amplitude"]),
    ("Marketing Analytics", "Business", ["marketing analytics", "customer segmentation", "churn analysis", "customer analytics"]),
    ("Financial Analysis", "Business", ["financial analysis", "financial modeling", "financial modelling"]),
    # ---- Soft skills
    ("Communication", "Soft Skills", ["communication skills", "communication", "verbal communication", "written communication", "presentation skills"]),
    ("Problem Solving", "Soft Skills", ["problem solving", "problem-solving", "analytical thinking", "critical thinking"]),
    ("Teamwork", "Soft Skills", ["teamwork", "collaboration", "cross-functional", "collaborative", "team player"]),
    ("Leadership", "Soft Skills", ["leadership", "mentoring", "team lead", "people management"]),
    ("Attention to Detail", "Soft Skills", ["attention to detail", "detail-oriented", "detail oriented"]),
]

# A skill on the resume that also proves another skill (credited as matched).
IMPLIES = {
    "Pandas": ["Python", "Data Analysis"],
    "NumPy": ["Python"],
    "SciPy": ["Python"],
    "Scikit-learn": ["Machine Learning", "Python"],
    "Matplotlib": ["Python", "Data Visualization"],
    "Seaborn": ["Python", "Data Visualization"],
    "Plotly": ["Data Visualization"],
    "Streamlit": ["Python"],
    "Flask": ["Python", "REST APIs"],
    "Django": ["Python"],
    "FastAPI": ["Python", "REST APIs"],
    "Advanced Excel": ["Excel"],
    "Deep Learning": ["Machine Learning"],
    "TensorFlow": ["Deep Learning", "Machine Learning"],
    "PyTorch": ["Deep Learning", "Machine Learning"],
    "Keras": ["Deep Learning", "Machine Learning"],
    "XGBoost": ["Machine Learning"],
    "NLP": ["Machine Learning"],
    "Computer Vision": ["Machine Learning"],
    "Hugging Face": ["NLP", "Deep Learning"],
    "LLMs": ["NLP"],
    "MySQL": ["SQL"],
    "PostgreSQL": ["SQL"],
    "SQL Server": ["SQL"],
    "Oracle DB": ["SQL"],
    "SQLite": ["SQL"],
    "BigQuery": ["SQL", "GCP", "Data Warehousing"],
    "Redshift": ["SQL", "AWS", "Data Warehousing"],
    "Snowflake": ["SQL", "Data Warehousing"],
    "Power BI": ["Data Visualization", "Business Intelligence"],
    "Tableau": ["Data Visualization", "Business Intelligence"],
    "Looker": ["Data Visualization", "Business Intelligence"],
    "Qlik": ["Data Visualization", "Business Intelligence"],
    "Apache Spark": ["Big Data"],
    "Hadoop": ["Big Data"],
    "Airflow": ["ETL"],
    "dbt": ["ETL", "SQL"],
    "Kubernetes": ["Docker"],
    "Time Series": ["Statistics"],
    "A/B Testing": ["Statistics"],
    "MLflow": ["Model Deployment"],
    "React": ["JavaScript"],
    "TypeScript": ["JavaScript"],
    "Node.js": ["JavaScript"],
}

# Close substitutes: knowing one gives a head start on another.
TRANSFERABLE_GROUPS = [
    {"Tableau", "Power BI", "Looker", "Qlik"},
    {"AWS", "Azure", "GCP"},
    {"PyTorch", "TensorFlow", "Keras"},
    {"MySQL", "PostgreSQL", "SQL Server", "Oracle DB", "SQLite"},
    {"Snowflake", "BigQuery", "Redshift", "Databricks"},
    {"Matplotlib", "Seaborn", "Plotly"},
    {"Airflow", "dbt", "Kafka"},
    {"Flask", "Django", "FastAPI"},
    {"Excel", "Advanced Excel"},
    {"MongoDB", "NoSQL", "Cassandra", "Redis"},
    {"Python", "R", "MATLAB", "SAS"},
    {"Java", "C#", "C++", "Kotlin"},
    {"Docker", "Kubernetes"},
    {"Jira", "Agile/Scrum", "Project Management"},
    {"Data Visualization", "Business Intelligence", "Reporting"},
]

# Learning guidance per category: (typical time to working proficiency, how to learn).
CATEGORY_LEARNING = {
    "Programming": ("4-8 weeks", "Follow a structured course, then build 2-3 small projects and solve practice problems."),
    "Databases": ("2-4 weeks", "Practise on a free sample database; write joins, aggregations, window functions and CTEs."),
    "Data Analysis": ("2-4 weeks", "Work through a real dataset end-to-end and document findings in a notebook."),
    "Visualization & BI": ("2-3 weeks", "Use the tool's free edition to rebuild a public dashboard and publish it in your portfolio."),
    "Machine Learning": ("4-8 weeks", "Take a hands-on course and complete one project with a written model report."),
    "Data Engineering": ("4-6 weeks", "Build a small batch pipeline locally, then orchestrate and schedule it."),
    "Cloud & DevOps": ("3-5 weeks", "Follow a fundamentals certification path and deploy a tiny project on the free tier."),
    "Software Engineering": ("3-6 weeks", "Build and ship a small project, writing tests and documentation along the way."),
    "Methodology": ("1-2 weeks", "Read the core guide and apply it to a personal or team project."),
    "Business": ("2-4 weeks", "Study 2-3 public case studies and practise writing a one-page insight summary."),
    "Soft Skills": ("ongoing", "Add concrete examples to your resume (scope, results, collaboration) rather than just the keyword."),
}

# Optional per-skill hints that override the generic category advice.
SKILL_TIPS = {
    "Tableau": "Learn calculated fields, LOD expressions and dashboard actions; publish 2 dashboards on Tableau Public.",
    "Power BI": "Learn Power Query, DAX measures and data modelling; build a report from a public dataset.",
    "AWS": "Cover IAM, S3, EC2, Lambda and RDS fundamentals; consider the AWS Cloud Practitioner certification.",
    "Azure": "Cover Blob Storage, VMs, Azure SQL and Functions; consider the AZ-900 fundamentals exam.",
    "GCP": "Cover BigQuery, Cloud Storage and Compute Engine; consider the Cloud Digital Leader certificate.",
    "Advanced Excel": "Master PivotTables, XLOOKUP / INDEX-MATCH, Power Query and dynamic arrays.",
    "SQL": "Master joins, GROUP BY, window functions, CTEs and query-optimisation basics.",
    "Python": "Learn core syntax, then pandas, NumPy and a plotting library through small data projects.",
    "Statistics": "Review descriptive stats, distributions, hypothesis tests, confidence intervals and regression.",
    "Machine Learning": "Learn the supervised workflow: split, train, cross-validate, tune and evaluate.",
    "Docker": "Containerise one of your projects with a Dockerfile and docker-compose.",
    "Git": "Practise branching, pull requests and resolving merge conflicts on GitHub.",
    "Apache Spark": "Learn the DataFrame API with PySpark on a local machine or Databricks Community Edition.",
    "Airflow": "Write a DAG with dependencies, retries and scheduling for a small ETL job.",
    "A/B Testing": "Learn power analysis, p-values, confidence intervals and common experiment pitfalls.",
    "LLMs": "Practise prompt design, embeddings and a simple retrieval-augmented generation (RAG) demo.",
}

# Short or generic aliases that must match with their original capitalisation
# (e.g. "Rust", "React", "SAS", "RAG") to avoid false positives like "rust on metal".
CASE_SENSITIVE_ALIASES = {"js", "rust", "swift", "torch", "lambda", "react", "sas", "spark", "transformers", "hive", "prophet", "rag", "express.js", "scala"}


def build_skill_index() -> dict:
    """Return {canonical: {"category": str, "aliases": [str]}}."""
    index = {}
    for name, cat, aliases in _RAW_SKILLS:
        extra = [] if len(name) <= 2 and name != "C#" else [name.lower()]  # never alias bare "r" / "go"
        index[name] = {"category": cat, "aliases": list(dict.fromkeys(aliases + extra))}
    return index


SKILLS = build_skill_index()
