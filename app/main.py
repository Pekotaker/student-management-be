from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import users, admin, teachers, students

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student Management System")

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(teachers.router, prefix="/teachers", tags=["teachers"])
app.include_router(students.router, prefix="/students", tags=["students"])

@app.get("/")
def root():
    return {"message": "Welcome to the Student Management System"}