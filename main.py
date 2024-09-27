from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4

app = FastAPI()

# Data models
class Student(BaseModel):
    id: Optional[str] = None
    name: str
    age: int
    email: str
    gpa: float

# In-memory database (list of students)
students_db = []

# Helper function to find student by ID
def get_student_by_id(student_id: str):
    for student in students_db:
        if student['id'] == student_id:
            return student
    return None

# Create a new student registration
@app.post("/students/register/", response_model=Student)
def register_student(student: Student):
    student.id = str(uuid4())  # Generate unique ID
    students_db.append(student.dict())
    return student

# Get the list of all registered students
@app.get("/students/", response_model=List[Student])
def get_students():
    return students_db

# Get a specific student by ID
@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: str):
    student = get_student_by_id(student_id)
    if student:
        return student
    raise HTTPException(status_code=404, detail="Student not found")

# Update student information
@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: str, updated_student: Student):
    student = get_student_by_id(student_id)
    if student:
        student.update(updated_student.dict(exclude_unset=True))
        return student
    raise HTTPException(status_code=404, detail="Student not found")

# Delete a student by ID
@app.delete("/students/{student_id}", response_model=dict)
def delete_student(student_id: str):
    student = get_student_by_id(student_id)
    if student:
        students_db.remove(student)
        return {"message": "Student deleted successfully"}
    raise HTTPException(status_code=404, detail="Student not found")

# Run the app with Uvicorn
# To run, use: uvicorn <filename>:app --reload
