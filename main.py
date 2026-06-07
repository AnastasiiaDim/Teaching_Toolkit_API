from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# 1. Initialize the app
app = FastAPI(title="Teaching Toolkit REST API")

#In-memory DB (lists of dictionaries for storaging the students and lessons, just for the test)
STUDENTS_DB = [
    {"id": 1, "name": "Max", "level": "B1", "lesson_price": 65},
    {"id": 2, "name": "Maria", "level": "B2", "lesson_price": 90},
    {"id": 3, "name": "Bob", "level": "A2", "lesson_price": 65}
]

LESSONS_DB = []

# 2. Validation Layers (Describe Pydantic Model)
# -----Students-----
class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Student name cannot be blank or longer than 100 characters")
    level: str = Field(..., min_length=1, description="Student level")
    lesson_price: float = Field(..., gt=0, description="Student lesson price cannot be less than 0")

# Response scheme
class StudentResponse(BaseModel):
    id: int
    name: str
    level: str
    lesson_price: float

# -----Lessons-----
class LessonCreate(BaseModel):
    student_id: int = Field(..., description="Student ID who had a class")
    date: str = Field(..., description="Lesson Date")

class LessonResponse(BaseModel):
    model_config = {"from_atributes": True}
    id: int
    student_id: int
    price_charged: float
    timestamp: datetime

# 3. Endpoints
# ------Students Endpoints------
# GET /students - get the list of all students
@app.get("/students", response_model=List[StudentResponse], status_code=status.HTTP_200_OK)
def get_all_students():
    return STUDENTS_DB

# POST /students - add a new student (with Pydantic Validation)
@app.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def add_student(student_data: StudentCreate):
    new_id = max((student["id"] for student in STUDENTS_DB), default=0) + 1
    new_student = student_data.model_dump()
    new_student["id"] = new_id

    STUDENTS_DB.append(new_student)
    return new_student

# GET /students/{id}- get specific student using ID (Path Parameter)
@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: int):
    for student in STUDENTS_DB:
        if student["id"] == student_id:
            return student

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Student with id {student_id} not found"
    )

# DELETE /students/{id} - delete the student by its id

@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int):
    for index, student in enumerate(STUDENTS_DB):
        if student["id"] == student_id:
            STUDENTS_DB.pop(index)
            return

    raise HTTPException(status_code=404,detail=f"Student with id {student_id} not found")

# GET /students/{id}/balance — Custom endpoint
# Count balance for a number of lessons (use Query parameter)
@app.get("/students/{student_id}/balance")
def calculate_balance(student_id: int, lessons: int = 1):
    if lessons < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number of lessons must be greater than or equal to zero"
        )

    for student in STUDENTS_DB:
        if student["id"] == student_id:
            total_balance = student["lesson_price"] * lessons
            return {
                "student_id": student_id,
                "name": student["name"],
                "level": student["level"],
                "total_balance": total_balance
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Student with id {student_id} not found"
    )

# ------Lessons Endpoints------
@app.get("/lessons", response_model=List[LessonResponse], status_code=status.HTTP_200_OK)
def get_lessons(student_id: Optional[int] = None):
    if student_id:
        return [lesson for lesson in LESSONS_DB if lesson["student_id"] == student_id]
    return LESSONS_DB
@app.post("/lessons", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def create_lesson(lessons_data: LessonCreate):
    # check if student exists
    target_student = None
    for student in STUDENTS_DB:
        if student["id"] == lessons_data.student_id:
            target_student = student
            break
    if not target_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {lessons_data.student_id} not found"
        )
    # count balance
    price = target_student["lesson_price"]

    # generate id for lesson saving
    new_lesson_id = LESSONS_DB[-1]["id"] + 1 if LESSONS_DB else 1

    # form a Lesson dictionary for saving in DB
    new_lesson = {
        "id": new_lesson_id,
        "student_id": lessons_data.student_id,
        "price_charged": price,
        "timestamp": datetime.now()
    }

    # save in in-memory DB
    LESSONS_DB.append(new_lesson)
    return new_lesson

