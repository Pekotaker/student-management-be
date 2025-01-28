from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/subject/{teacher_id}")
def get_subject(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    subject = db.query(models.Subject).filter(models.Subject.id == teacher.subject_id).first()
    return {"subject_id": subject.id, "subject_name": subject.name}

@router.get("/students/{teacher_id}")
def get_students(teacher_id: int, db: Session = Depends(get_db)):
    """
    Return all students of all classes that the teacher was assigned to.
    For each Student, also return user details like name, etc.
    """
    # 1. Find all class assignments for this teacher in teacher_class
    t_classes = db.query(models.TeacherClass).filter(models.TeacherClass.teacher_id == teacher_id).all()

    # If teacher not found or no assigned classes, return empty list
    if not t_classes:
        return []

    # 2. Collect all class_ids
    class_ids = [tc.class_id for tc in t_classes]

    # 3. Find all students whose class_id is in that list
    students = db.query(models.Student).filter(models.Student.class_id.in_(class_ids)).all()

    # Optionally join on user to get name or email
    # We'll just do multiple queries below for simplicity:
    result = []
    for s in students:
        user = db.query(models.User).filter(models.User.id == s.user_id).first()
        result.append({
            "student_id": s.id,
            "user_id": s.user_id,
            "student_name": user.name if user else "Unknown",
            "class_id": s.class_id
        })

    return result
@router.post("/register-teacher")
def register_teacher(user_id: int, subject_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    subject = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not user or not subject:
        raise HTTPException(status_code=404, detail="User or Subject not found")
    new_teacher = models.Teacher(user_id=user_id, subject_id=subject_id)
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    return {"teacher_id": new_teacher.id, "user_id": new_teacher.user_id, "subject_id": new_teacher.subject_id}

@router.post("/add-score")
def add_score(student_id: int, subject_id: int, score_value: str, teacher_id: str, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    subject = teacher.subject_id
    if not student or not teacher or not subject:
        raise HTTPException(status_code=404, detail="Student or Subject not found")
    new_score = models.Score(student_id=student_id, subject_id=subject_id, scores=score_value)
    db.add(new_score)
    db.commit()
    return {"message": "Score added successfully"}