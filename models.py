from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

from dotenv import load_dotenv
load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(15), nullable=False)
    enrollment = Column(String(20), unique=True, nullable=False)
    university = Column(String(100), nullable=False)
    course = Column(String(50), nullable=False)
    branch = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    skills = Column(Text)
    resume_path = Column(String(255), nullable=False)

# Create all tables
Base.metadata.create_all(bind=engine)