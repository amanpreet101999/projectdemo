from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from uuid import uuid4
import os

app = FastAPI()


DATABASE_URL = os.getenv("VERCEL_ENV", "postgresql://postgres:1234@localhost:5432/students")
# 
# Database connection settings (use your Vercel PostgreSQL connection string)
# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://students_owner:cnxwuJfr64YE@ep-billowing-hall-a5aq634s.us-east-2.aws.neon.tech/students?sslmode=require")


# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Student model
class StudentModel(Base):
    __tablename__ = 'students'
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    email = Column(String, unique=True, index=True)
    gpa = Column(Float)


# SQLAlchemy Teacher model
class TeacherModel(Base):
    __tablename__ = 'teachers'
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    email = Column(String, unique=True, index=True)
    subject = Column(String)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Pydantic schema for Student
class Student(BaseModel):
    id: Optional[str] = None
    name: str
    age: int
    email: str
    gpa: float

# Pydantic schema for Teacher
class Teacher(BaseModel):
    id: Optional[str] = None
    name: str
    age: int
    email: str
    subject: str

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD for Students

# Create a new student registration
@app.post("/students/register/", response_model=Student)
def register_student(student: Student, db: Session = Depends(get_db)):
    student_id = str(uuid4())  # Generate unique ID
    db_student = StudentModel(
        id=student_id,
        name=student.name,
        age=student.age,
        email=student.email,
        gpa=student.gpa
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

# Get the list of all registered students
@app.get("/students/", response_model=List[Student])
def get_students(db: Session = Depends(get_db)):
    return db.query(StudentModel).all()

# Get a specific student by ID
@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: str, db: Session = Depends(get_db)):
    student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# Update student information
@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: str, updated_student: Student, db: Session = Depends(get_db)):
    student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student.name = updated_student.name
    student.age = updated_student.age
    student.email = updated_student.email
    student.gpa = updated_student.gpa
    db.commit()
    db.refresh(student)
    return student

# Delete a student by ID
@app.delete("/students/{student_id}", response_model=dict)
def delete_student(student_id: str, db: Session = Depends(get_db)):
    student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}

# CRUD for Teachers

# Create a new teacher registration
@app.post("/teachers/register/", response_model=Teacher)
def register_teacher(teacher: Teacher, db: Session = Depends(get_db)):
    teacher_id = str(uuid4())  # Generate unique ID
    db_teacher = TeacherModel(
        id=teacher_id,
        name=teacher.name,
        age=teacher.age,
        email=teacher.email,
        subject=teacher.subject
    )
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

# Get the list of all registered teachers
@app.get("/teachers/", response_model=List[Teacher])
def get_teachers(db: Session = Depends(get_db)):
    return db.query(TeacherModel).all()

# Get a specific teacher by ID
@app.get("/teachers/{teacher_id}", response_model=Teacher)
def get_teacher(teacher_id: str, db: Session = Depends(get_db)):
    teacher = db.query(TeacherModel).filter(TeacherModel.id == teacher_id).first()
    if teacher is None:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher

# Update teacher information
@app.put("/teachers/{teacher_id}", response_model=Teacher)
def update_teacher(teacher_id: str, updated_teacher: Teacher, db: Session = Depends(get_db)):
    teacher = db.query(TeacherModel).filter(TeacherModel.id == teacher_id).first()
    if teacher is None:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    teacher.name = updated_teacher.name
    teacher.age = updated_teacher.age
    teacher.email = updated_teacher.email
    teacher.subject = updated_teacher.subject
    db.commit()
    db.refresh(teacher)
    return teacher

# Delete a teacher by ID
@app.delete("/teachers/{teacher_id}", response_model=dict)
def delete_teacher(teacher_id: str, db: Session = Depends(get_db)):
    teacher = db.query(TeacherModel).filter(TeacherModel.id == teacher_id).first()
    if teacher is None:
        raise HTTPException(status_code=404, detail="Teacher not found")
    db.delete(teacher)
    db.commit()
    return {"message": "Teacher deleted successfully"}
