from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Student(BaseModel):
    name: str
    age: int
    email: str

@app.post("/students/register/")
async def register_student(student: Student):
    return {"message": "Student registered successfully!", "student": student}
