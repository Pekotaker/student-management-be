from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
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
    """
    Return the subject of the teacher.
    """
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    subject = db.query(models.Subject).filter(models.Subject.id == teacher.subject_id).first()
    return {"subject_id": subject.id, "subject_name": subject.name}

@router.get("/classes/{teacher_id}")
def get_classes(teacher_id: int, db: Session = Depends(get_db)):
    """
    Return all classes that the teacher was assigned to.
    """
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    classes = db.query(models.Class).join(models.TeacherClass).filter(models.TeacherClass.teacher_id == teacher_id).all()
    if not classes:
        raise HTTPException(status_code=404, detail="No classes found for this teacher")
    # Return class details
    return [{"class_id": c.id, "class_name": c.name} for c in classes]    

@router.get("/students/{teacher_id}")
def get_students(teacher_id: int, db: Session = Depends(get_db)):
    """
    Return all students of all classes that the teacher was assigned to.
    For each Student, also return user details like name, etc.
    """
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

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
        class_obj = db.query(models.Class).filter(models.Class.id == s.class_id).first()
        scores = db.query(models.Score).filter(and_(models.Score.student_id == s.id, models.Score.subject_id == teacher.subject_id)).first()
        result.append({
            "student_id": s.id,
            "user_id": s.user_id,
            "student_name": user.name if user else "Unknown",
            "class_id": s.class_id,
            "class_name": class_obj.name if class_obj else "Unknown",
            "score": scores.scores if scores else None,
        })

    return result
@router.post("/register-teacher")
def register_teacher(user_id: int, subject_id: int, db: Session = Depends(get_db)):
    """"
    Register a teacher to a subject.
    """
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
def add_score(payload: dict, db: Session = Depends(get_db)):
    """"
    Add a score for a student.
    """
    student_id = payload.get("student_id")
    subject_id = payload.get("subject_id")
    score_value = payload.get("score_value")
    teacher_id = payload.get("teacher_id")

    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    subject = teacher.subject_id
    if not student or not teacher or not subject:
        raise HTTPException(status_code=404, detail="Student or Subject not found")
    # Check if the score already exists
    existing_score = db.query(models.Score).filter(and_(models.Score.student_id == student_id, models.Score.subject_id == subject_id)).first()
    if existing_score:
        # Update the existing score
        existing_score.scores = score_value
        db.commit()
        db.refresh(existing_score)
        return {"message": "Score updated successfully"}
    else:
        # Create a new score
        new_score = models.Score(student_id=student_id, subject_id=subject_id, scores=score_value)
        db.add(new_score)
        db.commit()
        db.refresh(new_score)
        return {"message": "Score added successfully"}