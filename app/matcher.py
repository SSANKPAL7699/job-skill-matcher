import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.skills_db import ALL_SKILLS, ALIASES, SKILLS


def normalize(text: str) -> str:
    """
    Step 1: Clean the text before we analyze it.
    
    Why? Because "Python," and "python" and "PYTHON" should all match.
    We lowercase everything and remove punctuation.
    
    Example:
    Input:  "Python, FastAPI & Docker!"
    Output: "python  fastapi   docker "
    """
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)  # replace punctuation with space
    text = re.sub(r"\s+", " ", text)       # collapse multiple spaces into one
    return text.strip()


def apply_aliases(text: str) -> str:
    """
    Step 2: Replace shorthand with full form.
    
    Why? Job descriptions often use abbreviations.
    We expand them so they match what's in our skills database.
    
    Example:
    Input:  "need ml engineer with nlp skills"
    Output: "need machine learning engineer with natural language processing skills"
    """
    words = text.split()
    result = []
    for word in words:
        # If word is in our aliases dict, replace it. Otherwise keep original.
        result.append(ALIASES.get(word, word))
    return " ".join(result)


def extract_skills(text: str) -> dict:
    """
    Step 3: Scan text and find all known tech skills.
    
    Why sort by length first?
    Because "machine learning" contains the word "machine" inside it.
    If we matched "machine" first, we'd get a false match.
    By matching longer phrases first, we catch "machine learning" as ONE skill
    before we accidentally match just "machine".
    
    Example:
    Input:  "I know machine learning and python"
    Output: {
        "ml_ai":     ["machine learning"],
        "languages": ["python"]
    }
    """
    # Clean the text first
    text = apply_aliases(normalize(text))
    
    found = {}  # stores skill → category pairs
    
    # Sort skills longest first so multi-word skills match before single words
    sorted_skills = sorted(ALL_SKILLS, key=lambda x: len(x["skill"]), reverse=True)
    
    for item in sorted_skills:
        skill = item["skill"]
        category = item["category"]
        
        # \b means "word boundary" - prevents "aws" matching inside "draws"
        # re.escape handles skills with special chars like "c++"
        pattern = r"\b" + re.escape(skill) + r"\b"
        
        if re.search(pattern, text):
            if skill not in found:
                found[skill] = category
    
    # Group found skills by category
    # e.g. {"languages": ["python", "java"], "cloud_devops": ["aws", "docker"]}
    by_category = {}
    for skill, category in found.items():
        by_category.setdefault(category, []).append(skill)
    
    return by_category


def compute_tfidf_similarity(resume: str, job_desc: str) -> float:
    """
    Step 4: Measure overall text similarity using TF-IDF + cosine similarity.
    
    This catches context BEYOND just skill keywords.
    For example, if a JD mentions "building scalable systems" and your resume
    says "designed high-scale architecture" — the skills won't keyword-match,
    but TF-IDF will still find similarity in the language used.
    
    ngram_range=(1,2) means we match:
    - Single words:  "python", "docker"
    - Two-word pairs: "machine learning", "rest api"
    
    Returns a float between 0.0 (no similarity) and 1.0 (identical)
    """
    vectorizer = TfidfVectorizer(
        stop_words="english",  # ignore "the", "and", "is" etc.
        ngram_range=(1, 2)     # match 1 and 2 word combinations
    )
    
    try:
        # Convert both texts into TF-IDF vectors
        tfidf_matrix = vectorizer.fit_transform([resume, job_desc])
        
        # Measure angle between the two vectors
        # Score of 1.0 = identical, 0.0 = completely different
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return float(similarity[0][0])
    except Exception:
        return 0.0


def match(resume_text: str, job_text: str) -> dict:
    """
    MAIN FUNCTION — this is what main.py calls.
    
    Takes resume + job description as plain text strings.
    Returns a complete analysis dictionary with scores, skills, and tips.
    
    The scoring works like this:
    
    Final Score = (Skill Score × 70%) + (TF-IDF Score × 30%)
    
    Why 70/30 split?
    Skill keywords are more reliable for job matching.
    TF-IDF adds context but can be noisy, so we weight it less.
    """

    # ── Step 1: Extract skills from both texts ──────────────────
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)
    
    # Flatten category dict into simple sets for easy comparison
    # {"languages": ["python"], "ml_ai": ["tensorflow"]} → {"python", "tensorflow"}
    resume_flat = set()
    for skills in resume_skills.values():
        resume_flat.update(skills)
    
    job_flat = set()
    for skills in job_skills.values():
        job_flat.update(skills)

    # ── Step 2: Compare the two skill sets ──────────────────────
    matched = resume_flat & job_flat    # & means intersection = skills in BOTH
    missing = job_flat - resume_flat    # - means difference = in JD but NOT resume
    bonus   = resume_flat - job_flat    # in resume but NOT required by JD

    # ── Step 3: Calculate skill match percentage ─────────────────
    # "What % of the job's required skills does your resume cover?"
    if len(job_flat) > 0:
        skill_score = len(matched) / len(job_flat) * 100
    else:
        skill_score = 0.0

    # ── Step 4: TF-IDF contextual similarity ────────────────────
    tfidf_score = compute_tfidf_similarity(resume_text, job_text) * 100

    # ── Step 5: Weighted final score ────────────────────────────
    final_score = round((skill_score * 0.7) + (tfidf_score * 0.3), 1)

    # ── Step 6: Assign a grade based on score ───────────────────
    if final_score >= 75:
        grade = "Strong Match"
        grade_color = "green"
    elif final_score >= 50:
        grade = "Good Match"
        grade_color = "blue"
    elif final_score >= 30:
        grade = "Partial Match"
        grade_color = "amber"
    else:
        grade = "Weak Match"
        grade_color = "red"

    # ── Step 7: Generate actionable tips ────────────────────────
    tips = []
    if missing:
        top_missing = list(missing)[:5]
        tips.append(
            f"Add these missing skills to your resume if you have them: "
            f"{', '.join(top_missing)}"
        )
    if final_score < 50:
        tips.append(
            "Tailor your resume bullet points to use exact keywords "
            "from the job description — many companies use ATS scanners."
        )
    if len(matched) > 0:
        tips.append(
            f"You already match {len(matched)} required skills — "
            f"make sure these are prominently listed on your resume."
        )
    if bonus:
        tips.append(
            f"You have {len(bonus)} bonus skills not listed in the JD — "
            f"these show breadth and can help you stand out."
        )

    # ── Step 8: Return everything ────────────────────────────────
    return {
        "final_score":    final_score,
        "skill_score":    round(skill_score, 1),
        "tfidf_score":    round(tfidf_score, 1),
        "grade":          grade,
        "grade_color":    grade_color,
        "matched_skills": sorted(list(matched)),
        "missing_skills": sorted(list(missing)),
        "bonus_skills":   sorted(list(bonus)),
        "resume_skills":  resume_skills,
        "job_skills":     job_skills,
        "tips":           tips,
        "total_jd_skills": len(job_flat),
        "total_matched":   len(matched),
    }