from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import Annotated
import os
from fastapi.templating import Jinja2Templates
from datetime import datetime
from database import get_db, create_student
from sqlalchemy.orm import Session
from models import Student,Base, engine
from dotenv import load_dotenv
import uuid



app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create static directory for resumes if it doesn't exist
os.makedirs("static/resumes", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
Base.metadata.create_all(bind=engine)

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
        # Check if email or enrollment already exists
        existing_student = db.query(Student).filter(
            (Student.email == email) | (Student.enrollment == enrollment)
        ).first()
        
        if existing_student:
            raise HTTPException(
                status_code=400,
                detail="Email or Enrollment Number already registered"
            )

        # Save the resume file
        file_ext = os.path.splitext(resume.filename)[1]
        if file_ext.lower() != '.pdf':
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed for resumes"
            )

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        resume_path = f"static/resumes/{unique_filename}"
        
        with open(resume_path, "wb") as buffer:
            buffer.write(await resume.read())

        # Prepare student data
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

        # Create student record
        create_student(db, student_data, resume_path)
        
        return JSONResponse(
            content={"message": "Student registered successfully"},
            status_code=200
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )

@app.get("/")
async def root(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("index.html", {"request": request})