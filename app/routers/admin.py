from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models, schemas
from ..utils.auth import hash_password, verify_password, create_access_token

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=schemas.UserOut)
def register_admin(admin_data: schemas.AdminCreate, db: Session = Depends(get_db)):
    existing_admin = db.query(models.AdminUser).filter(models.AdminUser.email == admin_data.email).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin email already registered"
        )
    hashed_pass = hash_password(admin_data.password)
    new_admin = models.AdminUser(
        email=admin_data.email,
        password=hashed_pass,
        name=admin_data.name
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return schemas.UserOut(id=new_admin.id, email=new_admin.email, name=new_admin.name)

@router.post("/login", response_model=schemas.Token)
def login_admin(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    admin_user = db.query(models.AdminUser).filter(models.AdminUser.email == credentials.email).first()
    if not admin_user or not verify_password(credentials.password, admin_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials"
        )
    access_token = create_access_token({"admin_id": admin_user.id, "role": "admin"}, 60)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/create-class")
def create_class(name: str, db: Session = Depends(get_db)):
    new_class = models.Class(name=name)
    db.add(new_class)
    db.commit()
    return {"id": new_class.id, "name": new_class.name}

@router.post("/assign-teacher-to-class")
def assign_teacher(teacher_id: int, class_id: int, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    class_obj = db.query(models.Class).filter(models.Class.id == class_id).first()
    if not teacher or not class_obj:
        raise HTTPException(status_code=404, detail="Teacher or Class not found")
    teacher_class = models.TeacherClass(teacher_id=teacher_id, class_id=class_id)
    db.add(teacher_class)
    db.commit()
    return {"message": "Teacher assigned to class successfully"}

@router.post("/create-schedule")
def create_schedule(class_id: int, time_slot: int, subject: str, db: Session = Depends(get_db)):
    schedule = models.Schedule(class_id=class_id, time_slot=time_slot, subject=subject)
    db.add(schedule)
    db.commit()
    return {"id": schedule.id, "class_id": schedule.class_id, "time_slot": schedule.time_slot, "subject": schedule.subject}