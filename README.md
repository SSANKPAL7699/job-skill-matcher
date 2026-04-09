# Job Skill Matcher

A tool that matches your resume against any job description and gives you an instant match score.

## Live Demo
👉 https://job-skill-matcher-production.up.railway.app

## What it does
- Upload your PDF resume or paste text
- Paste any job description
- Get a match score (0–100%)
- See matched skills, missing skills, and actionable tips

## How it works
- Extracts skills from both resume and JD using a curated database of 100+ tech skills
- Calculates skill overlap score (70% weight)
- Runs TF-IDF cosine similarity for contextual match (30% weight)
- Returns weighted final score with full breakdown

## Tech Stack
- Python
- FastAPI
- scikit-learn (TF-IDF + cosine similarity)
- Docker
- GitHub Actions (CI/CD)
- Deployed on Railway

## Run Locally
```bash
docker-compose up --build
```
Open http://localhost:8000

## API Usage
```bash
curl -X POST https://job-skill-matcher-production.up.railway.app/api/match \
  -H "Content-Type: application/json" \
  -d '{"resume": "Python developer...", "job_description": "Looking for..."}'
```

## Author
Shreya Sankpal — [LinkedIn](https://linkedin.com/in/shreya-sankpal) · [GitHub](https://github.com/SSANKPAL7699)
