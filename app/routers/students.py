from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register-student")
def register_student(user_id: int, class_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    class_obj = db.query(models.Class).filter(models.Class.id == class_id).first()
    if not user or not class_obj:
        raise HTTPException(status_code=404, detail="User or Class not found")
    new_student = models.Student(user_id=user_id, class_id=class_id)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return {"student_id": new_student.id, "user_id": new_student.user_id, "class_id": new_student.class_id}

@router.get("/scores/{user_id}")
def get_student_scores(user_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.user_id == user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    # scores = db.query(models.Score).filter(models.Score.student_id == student.id).all()
    # Join the tables to get the subject name
    scores = db.query(models.Score, models.Subject).join(models.Subject).filter(models.Score.student_id == student.id).all()
    return [{"subject": subj.name, "score": score.scores} for score, subj in scores]

@router.get("/schedule/{user_id}")
def get_student_schedule(user_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.user_id == user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    schedules = db.query(models.Schedule).filter(models.Schedule.class_id == student.class_id).all()
    return [{"time_slot": sch.time_slot, "subject": sch.subject} for sch in schedules]