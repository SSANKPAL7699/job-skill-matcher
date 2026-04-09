from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.matcher import match
from typing import Optional
import PyPDF2
import io

app = FastAPI(title="Job Skill Matcher", version="1.0.0")
templates = Jinja2Templates(directory="templates")


def extract_pdf_text(file_bytes: bytes) -> str:
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"PDF read error: {str(e)}")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/match", response_class=HTMLResponse)
async def match_form(
    request: Request,
    resume_text: Optional[str] = Form(default=""),
    resume_file: Optional[UploadFile] = File(default=None),
    job_description: Optional[str] = Form(default="")
):
    final_resume = ""
    error = None

    # Check job description first
    if not job_description or not job_description.strip():
        error = "Please paste a job description."
    else:
        # Try PDF upload first
        if resume_file and resume_file.filename and resume_file.filename != "":
            if not resume_file.filename.lower().endswith(".pdf"):
                error = "Please upload a PDF file only."
            else:
                try:
                    file_bytes = await resume_file.read()
                    if file_bytes:
                        final_resume = extract_pdf_text(file_bytes)
                        if not final_resume:
                            error = "Could not read PDF text. Try pasting your resume instead."
                    else:
                        error = "Uploaded file is empty."
                except Exception as e:
                    error = str(e)
        elif resume_text and resume_text.strip():
            final_resume = resume_text.strip()
        else:
            error = "Please upload a PDF or paste your resume text."

    if error:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": error,
            "job_description": job_description or ""
        })

    result = match(final_resume, job_description)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "result": result,
        "resume": final_resume[:500] + "..." if len(final_resume) > 500 else final_resume,
        "job_description": job_description
    })


@app.post("/api/match")
async def match_api(payload: dict):
    resume = payload.get("resume", "")
    job_description = payload.get("job_description", "")
    if not resume or not job_description:
        return {"error": "Both resume and job_description are required"}
    return match(resume, job_description)


@app.get("/health")
async def health():
    return {"status": "ok"}