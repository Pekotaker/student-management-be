# seed.py
import random
import string
import bcrypt
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

# Adjust these imports based on your actual project layout
from app.database import SessionLocal, engine
from app.models import (
    AdminUser, User, Subject, Teacher,
    Class, Student, TeacherClass, Score, Schedule
)

# ------------------------------
# CONFIGURABLES
# ------------------------------
NUM_ADMINS = 5
NUM_CLASSES = 10
MIN_STUDENTS_PER_CLASS = 18
MAX_STUDENTS_PER_CLASS = 22
NUM_SCHEDULES_PER_CLASS = 10
NUM_SUBJECTS = 10
SUBJECT_NAMES = [
    "Math", "Physics", "Chemistry", "English", "Literature",
    "Biology", "History", "Geography", "P.E", "Ethics"
]
NUM_TEACHERS = 40  # 4 teachers per subject
MAX_CLASSES_PER_TEACHER = 3

# Range for random scores
SCORE_MIN = 0.0
SCORE_MAX = 10.0
SCORE_STEP = 0.25

# A simple password we’ll hash for all seeded users
DEFAULT_PASSWORD = "password123"

# A global set to ensure we never reuse the same email
USED_EMAILS = set()


def generate_unique_email(base: str) -> str:
    """
    Generate a guaranteed-unique email of the form:
    {base}{suffix}@example.com

    We'll keep trying random 3-digit suffixes until we find one
    that's not in USED_EMAILS.
    """
    while True:
        suffix = "".join(random.choices(string.digits, k=3))
        email = f"{base}{suffix}@example.com".lower()
        if email not in USED_EMAILS:
            USED_EMAILS.add(email)
            return email


def random_date_of_birth():
    """
    Returns a random YYYY-MM-DD string for a plausible date of birth
    (between 1980 and 2012).
    """
    start_date = datetime(1980, 1, 1)
    end_date = datetime(2012, 12, 31)
    delta = end_date - start_date
    random_days = random.randrange(delta.days)
    birth_date = start_date + timedelta(days=random_days)
    return birth_date.strftime("%Y-%m-%d")


def random_name():
    """Generate a random name for demonstration."""
    first_names = ["John", "Jane", "Alice", "Bob", "Carol", "David", "Eve", "Frank", "Grace", "Heidi"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def hash_password(plain_text_password: str) -> str:
    """Hash the password with bcrypt."""
    return bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def wipe_db(db: Session):
    """Truncate all relevant tables before seeding."""
    db.execute("""
    TRUNCATE TABLE 
        teacher_class,
        scores,
        schedules,
        teachers,
        students,
        subjects,
        classes,
        users,
        admin_users
    RESTART IDENTITY CASCADE;
    """)
    db.commit()


def seed_database(db: Session):
    """
    Seed the database with:
      - 5 Admins
      - 10 Classes
      - 10 Subjects
      - 40 Teachers assigned up to 3 Classes
      - Students in each Class (18-22)
      - 10 Schedules per Class
      - Scores for each Student in each Subject
    """

    # 0) WIPE the DB tables
    print("Wiping database tables...")
    wipe_db(db)

    # 1) CREATE ADMINS
    print("Seeding AdminUsers...")
    for _ in range(NUM_ADMINS):
        name = random_name()
        admin = AdminUser(
            email=generate_unique_email("admin"),
            password=hash_password(DEFAULT_PASSWORD),
            name=name
        )
        db.add(admin)
    db.commit()

    # 2) CREATE SUBJECTS
    print("Seeding Subjects...")
    subjects = []
    for name in SUBJECT_NAMES:
        subj = Subject(name=name)
        db.add(subj)
        subjects.append(subj)
    db.commit()

    # 3) CREATE CLASSES
    print("Seeding Classes...")
    classes = []
    for i in range(NUM_CLASSES):
        class_name = f"Class {chr(ord('A') + i)}"
        new_class = Class(name=class_name)
        db.add(new_class)
        classes.append(new_class)
    db.commit()

    # 4) CREATE TEACHERS (40 total => 4 per subject), then assign them to classes
    print("Seeding Users & Teachers...")
    teachers = []
    sub_idx = 0
    for _ in range(NUM_TEACHERS):
        # Create a user for the teacher
        user_name = random_name()
        user = User(
            email=generate_unique_email("teacher"),
            password=hash_password(DEFAULT_PASSWORD),
            gender=random.choice(["M", "F"]),
            date_of_birth=random_date_of_birth(),
            name=user_name
        )
        db.add(user)
        db.flush()  # so user.id is available

        # Assign subject in round-robin style
        subject = subjects[sub_idx % len(subjects)]
        sub_idx += 1

        teacher = Teacher(
            user_id=user.id,
            subject_id=subject.id
        )
        db.add(teacher)
        teachers.append(teacher)
    db.commit()

    # TeacherClass assignments (each teacher up to 3 random classes)
    print("Assigning teachers to classes (up to 3 each)...")
    for teacher in teachers:
        num_classes = random.randint(1, MAX_CLASSES_PER_TEACHER)
        teacher_classes = random.sample(classes, num_classes)
        for c in teacher_classes:
            db.execute(
                """INSERT INTO teacher_class (class_id, teacher_id)
                   VALUES (:c_id, :t_id)""",
                {"c_id": c.id, "t_id": teacher.id}
            )
    db.commit()

    # 5) CREATE STUDENTS
    print("Seeding Students in each Class...")
    all_students = []
    for c in classes:
        num_students = random.randint(MIN_STUDENTS_PER_CLASS, MAX_STUDENTS_PER_CLASS)
        for _ in range(num_students):
            user_name = random_name()
            user = User(
                email=generate_unique_email("student"),
                password=hash_password(DEFAULT_PASSWORD),
                gender=random.choice(["M", "F"]),
                date_of_birth=random_date_of_birth(),
                name=user_name
            )
            db.add(user)
            db.flush()

            student = Student(
                user_id=user.id,
                class_id=c.id
            )
            db.add(student)
            all_students.append(student)
    db.commit()

    # 6) CREATE SCHEDULES (10 random schedules per class)
    print("Seeding Schedules...")
    for c in classes:
        for _ in range(NUM_SCHEDULES_PER_CLASS):
            day_num = random.randint(1, 5)  # 1=Mon, 5=Fri
            slot_num = random.randint(1, 7)
            chosen_subj = random.choice(subjects)
            new_sched = Schedule(
                date=str(day_num),
                class_id=c.id,
                time_slot=slot_num,
                subject=chosen_subj.name
            )
            db.add(new_sched)
    db.commit()

    # 7) CREATE SCORES for each student in each subject
    print("Seeding Scores for each student in each subject...")
    possible_scores = []
    cur = SCORE_MIN
    while cur <= SCORE_MAX + 0.0001:
        possible_scores.append(round(cur, 2))
        cur += SCORE_STEP

    for student in all_students:
        for subj in subjects:
            random_score = random.choice(possible_scores)
            score_entry = Score(
                student_id=student.id,
                subject_id=subj.id,
                scores=str(random_score)  # model is string
            )
            db.add(score_entry)
    db.commit()

    # 8) CREATE A DEFAULT ADMIN USER
    print("Creating a default AdminUser...")
    DEFAULT_ADMIN = AdminUser(
        email="admin@example.com",
        password=hash_password(DEFAULT_PASSWORD),
        name="Admin User"
    )

    db.add(DEFAULT_ADMIN)
    db.commit()

    print("Seeding complete!")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
