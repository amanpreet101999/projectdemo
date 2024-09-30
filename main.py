from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from uuid import uuid4 

# Database connection settings
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost:5432/students"


# SQLAlchemy setup
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

# SQLAlchemy Student model
class StudentModel(Base):
    __tablename__ = 'students'
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    email = Column(String, unique=True, index=True)
    gpa = Column(Float)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Pydantic schema for request/response
class Student(BaseModel):
    id: Optional[str] = None
    name: str
    age: int
    email: str
    gpa: float

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a new student registration
@app.post("/students/register/", response_model=Student)
def register_student(student: Student, db: Session = Depends(get_db)):
    db_student = StudentModel(
        id=str(uuid4()),  # Generate unique ID
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
