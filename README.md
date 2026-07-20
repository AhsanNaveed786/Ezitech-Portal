# Ezitech Internship Portal

Ezitech Internship Portal is a role-based internship management platform built with FastAPI and SQLAlchemy. It streamlines the internship workflow by providing dedicated dashboards and tools for Students, Mentors, Admins, and CEOs. The platform also includes an AI-powered mentor that offers personalized learning guidance based on each student's progress.

## Features

### Authentication & Authorization

- JWT-based authentication
- Role-based access control
- Separate login for Students, Mentors, Admins, and CEOs
- Secure password hashing

### Student

- Personalized dashboard
- Attendance tracking
- Leave application and history
- Project submission
- AI Mentor Chat
- AI Performance Dashboard
- Engineering Score
- Skill Growth Analysis
- Weak Areas Detection
- AI Recommendations
- Next Suggested Case Study

### Mentor

- Mentor dashboard
- View assigned students
- Review submitted projects
- Approve or reject projects
- View pending leave requests

### Admin

- Admin dashboard
- Manage students
- Manage mentors
- Attendance management
- Leave management
- Monitor platform activity

### CEO

- CEO dashboard
- Organization-wide statistics
- Student analytics
- Mentor analytics
- Attendance overview
- Leave overview
- Platform insights

## AI Features

The portal includes an AI Mentor powered by Groq's LLaMA 3.3 model.

Current capabilities include:

- Personalized programming assistance
- FastAPI guidance
- Python support
- SQL support
- Git & GitHub guidance
- Interview preparation
- Student-specific responses based on attendance, projects, and leave records
- AI-generated dashboard insights
- Personalized learning recommendations

## Tech Stack

### Backend

- FastAPI
- SQLAlchemy
- Pydantic
- JWT Authentication
- Passlib
- Uvicorn

### Database

- SQLite

### AI

- Groq API
- LLaMA 3.3 70B Versatile

## Project Structure

```
Ezitech Portal
│
├── backend
│   ├── models
│   ├── routers
│   ├── services
│   ├── schemas
│   └── database.py
│
├── utils
│   ├── jwt_handler.py
│   ├── security.py
│   ├── dependencies.py
│   └── groq.py
│
├── main.py
├── requirements.txt
└── .env
```

## Installation

Clone the repository.

```bash
git clone https://github.com/your-username/Ezitech-Portal.git
```

Navigate to the project directory.

```bash
cd Ezitech-Portal
```

Create a virtual environment.

```bash
python -m venv venv
```

Activate the virtual environment.

Windows

```bash
venv\Scripts\activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_groq_api_key
```

Run the server.

```bash
uvicorn main:app --reload
```

The API will be available at:

```
http://127.0.0.1:8000
```

Swagger Documentation:

```
http://127.0.0.1:8000/docs
```

## API Modules

- Authentication
- Student Dashboard
- Mentor Dashboard
- Admin Dashboard
- CEO Dashboard
- Attendance
- Leave Management
- Project Management
- AI Mentor
- AI Dashboard

## Future Improvements

- Retrieval-Augmented Generation (RAG)
- Resume Review using AI
- GitHub Repository Analysis
- Mock Interview Agent
- Coding Assessment
- Learning Roadmaps
- Progress Analytics
- Certificate Generation
- Email Notifications
- Deployment with Docker

## Implementation of Ai Agents in 
all dashboards
