import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.skills_db import ALL_SKILLS, ALIASES, SKILLS


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def apply_aliases(text: str) -> str:
    words = text.split()
    result = []
    for word in words:
        result.append(ALIASES.get(word, word))
    return " ".join(result)


def extract_skills(text: str) -> dict:
    text = apply_aliases(normalize(text))
    found = {}
    sorted_skills = sorted(ALL_SKILLS, key=lambda x: len(x["skill"]), reverse=True)
    for item in sorted_skills:
        skill = item["skill"]
        category = item["category"]
        # Skip single letter skills like "c", "r" — too many false positives
        if len(skill) <= 1:
            continue
        # For very short skills (2-3 chars like "go", "aws") require word boundary
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text):
            if skill not in found:
                found[skill] = category
    by_category = {}
    for skill, category in found.items():
        by_category.setdefault(category, []).append(skill)
    return by_category


def compute_tfidf_similarity(resume: str, job_desc: str) -> float:
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1
    )
    try:
        tfidf_matrix = vectorizer.fit_transform([resume, job_desc])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return float(similarity[0][0])
    except Exception:
        return 0.0


def is_tech_document(text: str) -> bool:
    """
    Check if the text looks like a tech resume at all.
    If fewer than 2 known tech skills are found, it's probably
    not a tech resume — flag it as invalid input.
    """
    text_normalized = apply_aliases(normalize(text))
    tech_count = 0
    for item in ALL_SKILLS:
        skill = item["skill"]
        if item["category"] in ["languages", "ml_ai", "web_frameworks",
                                  "cloud_devops", "databases"]:
            if len(skill) <= 1:
                continue
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text_normalized):
                tech_count += 1
        if tech_count >= 2:
            return True
    return False


def is_tech_job(text: str) -> bool:
    """
    Check if the job description is a tech role.
    Sales manager, DMV, etc. should not get tech scores.
    """
    text_normalized = normalize(text)
    tech_count = 0
    for item in ALL_SKILLS:
        skill = item["skill"]
        if item["category"] in ["languages", "ml_ai", "web_frameworks",
                                  "cloud_devops", "databases"]:
            if len(skill) <= 1:
                continue
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text_normalized):
                tech_count += 1
        if tech_count >= 2:
            return True
    return False


def match(resume_text: str, job_text: str) -> dict:

    # ── Validate inputs ──────────────────────────────────────────
    warning = None

    if not is_tech_document(resume_text):
        warning = "Your resume doesn't appear to contain technical skills. Results may not be meaningful."

    if not is_tech_job(job_text):
        warning = "This job description doesn't appear to be a technical role. This tool is designed for software/tech jobs."

    # ── Extract skills ───────────────────────────────────────────
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)

    resume_flat = set()
    for skills in resume_skills.values():
        resume_flat.update(skills)

    job_flat = set()
    for skills in job_skills.values():
        job_flat.update(skills)

    matched = resume_flat & job_flat
    missing = job_flat - resume_flat
    bonus   = resume_flat - job_flat

    # ── Skill score ──────────────────────────────────────────────
    if len(job_flat) > 0:
        skill_score = len(matched) / len(job_flat) * 100
    else:
        skill_score = 0.0

    # ── TF-IDF score — penalize if job has no tech skills ────────
    tfidf_score = compute_tfidf_similarity(resume_text, job_text) * 100

    # If the job description has no tech skills, cap tfidf contribution
    if len(job_flat) == 0:
        tfidf_score = tfidf_score * 0.1

    # ── Final score ──────────────────────────────────────────────
    final_score = round((skill_score * 0.7) + (tfidf_score * 0.3), 1)

    # ── Grade ────────────────────────────────────────────────────
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

    # ── Tips ─────────────────────────────────────────────────────
    tips = []
    if warning:
        tips.insert(0, f"⚠️ {warning}")
    if missing:
        top_missing = list(missing)[:5]
        tips.append(f"Add these missing skills to your resume if you have them: {', '.join(top_missing)}")
    if final_score < 50:
        tips.append("Tailor your resume bullet points to use exact keywords from the job description.")
    if len(matched) > 0:
        tips.append(f"You already match {len(matched)} required skills — make sure these are prominently listed.")
    if bonus:
        tips.append(f"You have {len(bonus)} bonus skills not listed in the JD — these show breadth.")

    return {
        "final_score":     final_score,
        "skill_score":     round(skill_score, 1),
        "tfidf_score":     round(tfidf_score, 1),
        "grade":           grade,
        "grade_color":     grade_color,
        "matched_skills":  sorted(list(matched)),
        "missing_skills":  sorted(list(missing)),
        "bonus_skills":    sorted(list(bonus)),
        "resume_skills":   resume_skills,
        "job_skills":      job_skills,
        "tips":            tips,
        "total_jd_skills": len(job_flat),
        "total_matched":   len(matched),
        "warning":         warning,
    }