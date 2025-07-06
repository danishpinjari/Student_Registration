from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Annotated
import os
import uuid
import logging

from database import get_db, create_student
from models import Student, Base, engine

# Load environment variables only in local development
if os.getenv("RENDER") != "true":
    from dotenv import load_dotenv
    load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static directory for uploaded resumes
os.makedirs("static/resumes", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

#  Templates directory
templates = Jinja2Templates(directory="templates")

#  Create all tables
Base.metadata.create_all(bind=engine)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#  Register student route
@app.post("/register-student")
async def register_student(
    name: Annotated[str, Form()],
    email: Annotated[str, Form()],
    phone: Annotated[str, Form()],
    enrollment: Annotated[str, Form()],
    university: Annotated[str, Form()],
    course: Annotated[str, Form()],
    branch: Annotated[str, Form()],
    year: Annotated[str, Form()],
    skills: Annotated[str, Form()] = "",
    resume: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Received registration for: {name} - {email}")

        # Check if email or enrollment already exists
        existing_student = db.query(Student).filter(
            (Student.email == email) | (Student.enrollment == enrollment)
        ).first()
        
        if existing_student:
            raise HTTPException(
                status_code=400,
                detail="Email or Enrollment Number already registered"
            )

        # Check file type
        file_ext = os.path.splitext(resume.filename)[1]
        if file_ext.lower() != '.pdf':
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed for resumes"
            )

        # Generate unique resume filename
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        resume_path = f"static/resumes/{unique_filename}"
        
        # Save the uploaded resume
        with open(resume_path, "wb") as buffer:
            buffer.write(await resume.read())

        # Prepare and insert student data
        student_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'enrollment': enrollment,
            'university': university,
            'course': course,
            'branch': branch,
            'year': int(year),
            'skills': skills
        }

        create_student(db, student_data, resume_path)

        return JSONResponse(
            content={"message": "Student registered successfully"},
            status_code=200
        )

    except HTTPException as he:
        logger.error(f"HTTPException: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )

# Root route renders index page
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
