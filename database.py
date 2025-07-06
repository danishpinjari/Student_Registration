from sqlalchemy.orm import Session
from models import Student, SessionLocal
import os
from dotenv import load_dotenv

# Only load .env locally
if os.getenv("RENDER") != "true":
    load_dotenv()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_student(db: Session, student_data: dict, resume_path: str):
    db_student = Student(
        name=student_data['name'],
        email=student_data['email'],
        phone=student_data['phone'],
        enrollment=student_data['enrollment'],
        university=student_data['university'],
        course=student_data['course'],
        branch=student_data['branch'],
        year=student_data['year'],
        skills=student_data.get('skills', ''),
        resume_path=resume_path
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student
