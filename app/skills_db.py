# This file is our skills knowledge base.
# Think of it like a dictionary that knows about every tech skill.
# We group skills by category so we can show recruiters
# exactly which skill AREAS are matching, not just random words.

SKILLS = {
    "languages": [
        "python", "java", "javascript", "typescript", "c++", "c", "kotlin",
        "swift", "go", "rust", "r", "scala", "php", "ruby", "bash", "shell",
        "sql", "html", "css", "abap"
    ],
    "ml_ai": [
        "machine learning", "deep learning", "nlp", "natural language processing",
        "computer vision", "scikit-learn", "sklearn", "tensorflow", "pytorch",
        "keras", "xgboost", "lightgbm", "pandas", "numpy", "matplotlib",
        "seaborn", "hugging face", "transformers", "bert", "gpt", "llm",
        "reinforcement learning", "neural network", "regression", "classification",
        "clustering", "feature engineering", "model deployment", "mlflow",
        "data science", "statistical analysis", "a/b testing", "hypothesis testing",
        "tfidf", "tf-idf", "word2vec", "random forest", "naive bayes",
        "logistic regression", "linear regression", "svm", "knn"
    ],
    "web_frameworks": [
        "fastapi", "flask", "django", "react", "react native", "angular",
        "vue", "node.js", "nodejs", "express", "spring boot", "spring",
        "rest api", "restful", "graphql", "microservices", "bootstrap"
    ],
    "databases": [
        "postgresql", "mysql", "mongodb", "redis", "sqlite", "oracle",
        "dynamodb", "cassandra", "elasticsearch", "firebase", "supabase",
        "sql server", "nosql", "hana", "sap hana"
    ],
    "cloud_devops": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
        "terraform", "ansible", "jenkins", "github actions", "ci/cd",
        "circleci", "gitlab", "linux", "nginx", "ec2", "s3", "lambda",
        "elastic beanstalk", "cloud formation", "devops", "sre"
    ],
    "tools": [
        "git", "github", "jira", "agile", "scrum", "postman", "swagger",
        "jupyter", "vscode", "xcode", "android studio", "figma",
        "tableau", "power bi", "airflow", "kafka", "spark", "hadoop"
    ],
    "soft_skills": [
        "communication", "leadership", "teamwork", "problem solving",
        "analytical", "collaboration", "project management"
    ]
}

# Flatten all skills into one list for easy searching later
# Instead of searching category by category, we can search everything at once
# Result looks like: [{"skill": "python", "category": "languages"}, ...]
ALL_SKILLS = []
for category, skills in SKILLS.items():
    for skill in skills:
        ALL_SKILLS.append({"skill": skill, "category": category})

# Aliases — shorthand terms that mean the same thing
# e.g. if a job description says "ML engineer" we treat "ML" as "machine learning"
# This prevents us from missing a match just because someone used an abbreviation
ALIASES = {
    "ml": "machine learning",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "k8s": "kubernetes",
    "gcp": "google cloud",
    "tf": "tensorflow",
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "sklearn": "scikit-learn",
}