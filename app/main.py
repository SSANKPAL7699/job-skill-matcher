from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.matcher import match

# ── Create the FastAPI app ───────────────────────────────────────
# Think of this like turning on a web server.
# The title and description show up in the auto-generated API docs at /docs
app = FastAPI(
    title="Job Skill Matcher",
    description="Match your resume against any job description. Get a score, matched skills, and missing skills.",
    version="1.0.0"
)

# ── Tell FastAPI where our HTML files live ───────────────────────
# Jinja2Templates is the bridge between Python and HTML.
# It lets us inject Python variables into our HTML page.
# "directory='templates'" tells it to look in our templates/ folder.
templates = Jinja2Templates(directory="templates")


# ── Route 1: Home page ───────────────────────────────────────────
# What is a route? It's a URL path that does something.
# When someone visits http://localhost:8000/ this function runs.
# @app.get means this route responds to GET requests
# (GET = browser just loading a page, no data sent)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Just shows the empty form when someone first visits the site.
    We pass 'request' to the template — Jinja2 always needs this.
    """
    return templates.TemplateResponse("index.html", {"request": request})


# ── Route 2: Form submission ─────────────────────────────────────
# @app.post means this route responds to POST requests
# (POST = user submitting a form with data)
# When user clicks "Analyze Match" button, this runs.
@app.post("/match", response_class=HTMLResponse)
async def match_form(
    request: Request,
    resume: str = Form(...),           # grabs "resume" field from the form
    job_description: str = Form(...)   # grabs "job_description" field from the form
    # The ... means these fields are REQUIRED — app will error if they're empty
):
    """
    1. Receives resume + job_description text from the HTML form
    2. Passes them to our matcher.py match() function
    3. Sends the results back to the same HTML page to display
    """
    result = match(resume, job_description)
    
    # We send back:
    # - request (required by Jinja2)
    # - result (the match analysis from matcher.py)
    # - resume + job_description (so the text stays in the boxes after submit)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "result": result,
        "resume": resume,
        "job_description": job_description
    })


# ── Route 3: JSON API endpoint ───────────────────────────────────
# This is for developers who want to use our matcher programmatically
# instead of through the browser UI.
# 
# Example: a Chrome extension could call this API silently
# while you browse LinkedIn jobs and show you a match score.
#
# How to test this:
# curl -X POST http://localhost:8000/api/match \
#   -H "Content-Type: application/json" \
#   -d '{"resume": "Python developer...", "job_description": "Need Python..."}'
@app.post("/api/match")
async def match_api(payload: dict):
    """
    Pure JSON API — no HTML, just raw data back and forth.
    Useful for building other tools on top of our matcher.
    """
    resume = payload.get("resume", "")
    job_description = payload.get("job_description", "")
    
    if not resume or not job_description:
        return {"error": "Both resume and job_description fields are required"}
    
    return match(resume, job_description)


# ── Route 4: Health check ────────────────────────────────────────
# This is a standard route every production API should have.
# Docker, AWS, and monitoring tools ping this URL to check
# if the app is alive and running.
# If it returns {"status": "ok"} the app is healthy.
# If it doesn't respond, something is wrong.
@app.get("/health")
async def health():
    return {"status": "ok"}