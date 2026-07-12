from fastapi import FastAPI
from backend.database import engine
from backend.models import Student, Mentor, Attendance
from backend.models import Base


Base.metadata.create_all(bind=engine)

app = FastAPI()
@app.get("/")
def home():
    return {"message": "Hello, World!"}     

@app.get("/student")
def student():
    return {"message": "Hello, Student!"}

@app.get("/admin")
def admin():
    return {"message": "Hello, Admin!"}

@app.get("/ceo")
def ceo():
    return {"message": "Hello, CEO!"}
