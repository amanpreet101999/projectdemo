from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4

app = FastAPI()

# In-memory storage for students
students_db = {}

# Pydantic schema for request/response
class Student(BaseModel):
    id: Optional[str] = None
    name: str
    age: int
    email: str
    gpa: float

# Create a new student registration
@app.post("/students/register/", response_model=Student)
def register_student(student: Student):
    student_id = str(uuid4())  # Generate unique ID
    student.id = student_id
    students_db[student_id] = student
    return student

# Get the list of all registered students
@app.get("/students/", response_model=List[Student])
def get_students():
    return list(students_db.values())

# Get a specific student by ID
@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: str):
    student = students_db.get(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# Update student information
@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: str, updated_student: Student):
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    updated_student.id = student_id  # Keep the same ID
    students_db[student_id] = updated_student
    return updated_student

# Delete a student by ID
@app.delete("/students/{student_id}", response_model=dict)
def delete_student(student_id: str):
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    del students_db[student_id]
    return {"message": "Student deleted successfully"}
