from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.matcher import match
import PyPDF2
import io

app = FastAPI(
    title="Job Skill Matcher",
    description="Match your resume against any job description.",
    version="1.0.0"
)

templates = Jinja2Templates(directory="templates")


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Takes raw PDF bytes and extracts all text from it.
    
    How it works:
    1. PyPDF2 reads the PDF structure
    2. It goes page by page and pulls out the text
    3. We join all pages into one big string
    
    Why io.BytesIO?
    PyPDF2 expects a file-like object, not raw bytes.
    io.BytesIO wraps raw bytes into something that behaves like a file
    so PyPDF2 can read it without saving to disk first.
    """
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/match", response_class=HTMLResponse)
async def match_form(
    request: Request,
    resume_text: str = Form(""),
    resume_file: UploadFile = File(None),
    job_description: str = Form(default="")
):
    """
    Now accepts EITHER:
    - A pasted resume text (resume_text field)
    - An uploaded PDF file (resume_file field)
    
    If both are provided, the uploaded file takes priority.
    If neither is provided, we show an error.
    """
    # Try to get resume text from uploaded PDF first
    final_resume = ""
    error = None

    if resume_file and resume_file.filename:
        # User uploaded a file
        if not resume_file.filename.endswith(".pdf"):
            error = "Please upload a PDF file only."
        else:
            try:
                file_bytes = await resume_file.read()
                final_resume = extract_text_from_pdf(file_bytes)
                if not final_resume:
                    error = "Could not extract text from PDF. Try pasting your resume instead."
            except Exception as e:
                error = f"Error reading PDF: {str(e)}"
    elif resume_text.strip():
        # User pasted text
        final_resume = resume_text.strip()
    else:
        error = "Please either upload your resume PDF or paste your resume text."

    if error:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": error,
            "job_description": job_description
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