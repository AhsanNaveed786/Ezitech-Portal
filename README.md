# 🎓 Ezitech Internship Portal

A modern, role-based internship management platform that streamlines the entire internship workflow. Built with **FastAPI**, **SQLAlchemy**, and **AI-powered features** using Groq's LLaMA model.

---

## ✨ Key Features

### 🔐 Authentication & Security
- JWT-based token authentication
- Role-based access control (Students, Mentors, Admins, CEOs)
- Secure password hashing with Passlib
- Separate login endpoints for each role

### 👨‍🎓 Student Features
- **Personal Dashboard** - View overall progress and statistics
- **Attendance Tracking** - Track daily attendance with visual reports
- **Leave Management** - Apply for leaves and view history
- **Project Submissions** - Submit and track project work
- **AI Mentor Chat** - Get personalized AI assistance for coding, interviews, and learning
- **Performance Dashboard** - View engineering score and skill growth
- **Progress Analytics** - Weak areas detection and improvement recommendations
- **AI Suggestions** - Next suggested case studies and learning paths

### 👨‍🏫 Mentor Features
- **Mentor Dashboard** - Overview of assigned students
- **Student Management** - View all assigned students and their progress
- **Project Review** - Review, approve, or reject submitted projects
- **Leave Approvals** - Manage pending leave requests
- **Performance Tracking** - Monitor student progress and engagement
- **Feedback System** - Provide personalized feedback to students

### 🛡️ Admin Features
- **Admin Dashboard** - Platform-wide management controls
- **Student Management** - Add, edit, remove students
- **Mentor Management** - Manage mentor accounts and assignments
- **Attendance Management** - Override or correct attendance records
- **Leave Management** - Approve or reject leave requests
- **Activity Monitoring** - Track platform usage and activities
- **System Configuration** - Manage platform settings

### 👔 CEO Features
- **Executive Dashboard** - High-level organizational insights
- **Student Analytics** - Overall student performance metrics
- **Mentor Analytics** - Mentor performance and effectiveness
- **Attendance Overview** - Organization-wide attendance statistics
- **Leave Overview** - Comprehensive leave management data
- **Platform Insights** - Key performance indicators and trends
- **Reports** - Generate detailed reports on internship program

### 🤖 AI Mentor (Powered by Groq LLaMA 3.3)
The AI Mentor provides intelligent, personalized assistance:
- **Programming Help** - Python, FastAPI, SQL guidance
- **Framework Support** - Framework-specific tutorials and solutions
- **Git & GitHub** - Version control and collaboration help
- **Interview Prep** - Coding interview and HR interview preparation
- **Student Context** - AI responses consider attendance, projects, and performance
- **Learning Paths** - Personalized recommendations based on weak areas
- **Dashboard Insights** - AI-generated performance summaries

---

## 🛠️ Tech Stack

### Backend
```
FastAPI          - Modern web framework
SQLAlchemy       - ORM for database operations
Pydantic         - Data validation
JWT              - Secure token authentication
Passlib          - Password hashing
Uvicorn          - ASGI server
```

### Database
```
SQLite           - Lightweight, file-based database
```

### AI Integration
```
Groq API         - LLaMA 3.3 70B Versatile model
```

---

## 📁 Project Structure

```
ezitech-internship-portal/
│
├── backend/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── student.py
│   │   ├── mentor.py
│   │   ├── project.py
│   │   ├── attendance.py
│   │   └── leave.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── students.py
│   │   ├── mentors.py
│   │   ├── admins.py
│   │   ├── ceos.py
│   │   ├── projects.py
│   │   ├── attendance.py
│   │   ├── leaves.py
│   │   └── ai_mentor.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── student.py
│   │   ├── project.py
│   │   └── responses.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── student_service.py
│   │   ├── mentor_service.py
│   │   ├── admin_service.py
│   │   ├── ceo_service.py
│   │   ├── ai_service.py
│   │   └── analytics_service.py
│   │
│   └── database.py
│
├── utils/
│   ├── __init__.py
│   ├── jwt_handler.py
│   ├── security.py
│   ├── dependencies.py
│   ├── groq.py
│   └── exceptions.py
│
├── main.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Groq API key (get it from [Groq Console](https://console.groq.com))

### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/ezitech-internship-portal.git
cd ezitech-internship-portal
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Create Environment File
Create a `.env` file in the project root:
```env
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# JWT Configuration
SECRET_KEY=your_super_secret_key_change_this_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./ezitech.db

# Server
DEBUG=True
```

### Step 5: Run Server
```bash
uvicorn main:app --reload
```

The application will start at:
- **API**: `http://127.0.0.1:8000`
- **Docs (Swagger UI)**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

---

## 📋 API Endpoints Overview

### Authentication
```
POST   /api/auth/login                 - User login (Students/Mentors/Admins/CEOs)
POST   /api/auth/register              - User registration
POST   /api/auth/refresh-token         - Refresh access token
POST   /api/auth/logout                - Logout user
```

### Student Dashboard
```
GET    /api/students/dashboard         - Student dashboard data
GET    /api/students/profile           - Student profile
PUT    /api/students/profile           - Update student profile
GET    /api/students/performance       - Performance metrics
GET    /api/students/skills            - Skill analysis
GET    /api/students/recommendations   - AI recommendations
```

### Projects
```
GET    /api/projects/list              - List all projects
POST   /api/projects/submit            - Submit project
GET    /api/projects/{id}              - Get project details
PUT    /api/projects/{id}              - Update project
GET    /api/projects/my-submissions    - Student's submissions
GET    /api/projects/pending-review    - Mentor's pending reviews
POST   /api/projects/{id}/approve      - Approve project
POST   /api/projects/{id}/reject       - Reject project
```

### Attendance
```
GET    /api/attendance/list            - Get attendance records
POST   /api/attendance/mark            - Mark attendance
GET    /api/attendance/report          - Attendance report
GET    /api/attendance/statistics      - Attendance stats
```

### Leave Management
```
GET    /api/leaves/list                - List all leaves
POST   /api/leaves/apply               - Apply for leave
GET    /api/leaves/my-requests         - My leave requests
PUT    /api/leaves/{id}                - Update leave request
POST   /api/leaves/{id}/approve        - Approve leave
POST   /api/leaves/{id}/reject         - Reject leave
```

### AI Mentor
```
POST   /api/ai/chat                    - Chat with AI mentor
GET    /api/ai/chat-history            - Get chat history
POST   /api/ai/dashboard-insights      - Get AI-generated dashboard
GET    /api/ai/recommendations         - Get learning recommendations
POST   /api/ai/interview-prep          - Interview preparation
```

### Mentor Dashboard
```
GET    /api/mentors/dashboard          - Mentor dashboard
GET    /api/mentors/students           - Assigned students
GET    /api/mentors/pending-tasks      - Pending reviews/leaves
PUT    /api/mentors/students/{id}      - Update student feedback
```

### Admin Dashboard
```
GET    /api/admin/dashboard            - Admin dashboard
GET    /api/admin/users                - Manage users
POST   /api/admin/users                - Create user
PUT    /api/admin/users/{id}           - Edit user
DELETE /api/admin/users/{id}           - Delete user
GET    /api/admin/activity-log         - Platform activity
PUT    /api/admin/settings             - System settings
```

### CEO Dashboard
```
GET    /api/ceo/dashboard              - Executive dashboard
GET    /api/ceo/analytics/students     - Student analytics
GET    /api/ceo/analytics/mentors      - Mentor analytics
GET    /api/ceo/reports/attendance     - Attendance reports
GET    /api/ceo/reports/performance    - Performance reports
GET    /api/ceo/reports/kpis           - KPI metrics
```

---

## 🗄️ Database Models

### User Model
```
- id (Primary Key)
- username (Unique)
- email (Unique)
- password (Hashed)
- full_name
- role (student/mentor/admin/ceo)
- is_active
- created_at
- updated_at
```

### Student Model
```
- id (Primary Key)
- user_id (Foreign Key)
- mentor_id (Foreign Key)
- enrollment_date
- attendance_percentage
- total_projects
- completed_projects
- current_skills
- weak_areas
```

### Mentor Model
```
- id (Primary Key)
- user_id (Foreign Key)
- specialization
- students_assigned
- projects_reviewed
- avg_rating
```

### Project Model
```
- id (Primary Key)
- student_id (Foreign Key)
- title
- description
- submission_date
- status (pending/approved/rejected)
- mentor_feedback
- score
```

### Attendance Model
```
- id (Primary Key)
- student_id (Foreign Key)
- date
- status (present/absent/late)
- marked_by (mentor_id)
```

### Leave Model
```
- id (Primary Key)
- student_id (Foreign Key)
- start_date
- end_date
- reason
- status (pending/approved/rejected)
- approved_by (mentor_id)
```

---

## 🤖 AI Mentor Integration

### How It Works
1. **Student Context**: The AI considers student's attendance, projects, and performance
2. **Personalized Responses**: Generates contextual answers based on student level
3. **Learning Paths**: Recommends next topics based on weak areas
4. **Interview Prep**: Provides mock interview questions and solutions
5. **Dashboard Insights**: Generates AI-powered performance summaries

### Example AI Features
```python
# Chat with AI
POST /api/ai/chat
{
    "message": "Help me understand FastAPI middleware",
    "context": "programming"
}

# Get Dashboard Insights
GET /api/ai/dashboard-insights
Response: AI-generated summary of performance and recommendations

# Interview Preparation
POST /api/ai/interview-prep
{
    "interview_type": "coding",
    "topics": ["arrays", "strings", "dynamic programming"]
}
```

---

## 🔑 User Roles & Permissions

### Student
- View own dashboard and profile
- Submit projects
- Apply for leaves
- Track attendance
- Chat with AI mentor
- View performance analytics
- Cannot: Approve projects, manage other users

### Mentor
- View assigned students
- Review and approve/reject projects
- Approve/reject leave requests
- Track student progress
- Provide feedback
- Cannot: Manage other mentors, access CEO features

### Admin
- Full platform management
- User management (create/edit/delete)
- Attendance & leave override
- Activity monitoring
- System configuration
- Cannot: Access CEO analytics

### CEO
- View organization-wide analytics
- Access executive dashboard
- Generate reports
- Monitor key metrics
- Cannot: Modify user data, manage daily operations

---

## 🔐 Security Features

- **Password Hashing**: Passwords hashed with bcrypt
- **JWT Tokens**: Secure token-based authentication
- **Role-Based Access**: Endpoints protected by roles
- **Token Expiration**: Automatic token expiration and refresh
- **SQL Injection Prevention**: SQLAlchemy ORM prevents SQL injection
- **CORS Configuration**: Configurable CORS for frontend integration

---

## 📊 Future Enhancements

- [ ] **RAG (Retrieval-Augmented Generation)** - Enhanced AI with knowledge base
- [ ] **Resume Review** - AI-powered resume analysis and feedback
- [ ] **GitHub Analysis** - Automatic code quality analysis from GitHub repos
- [ ] **Mock Interview Agent** - Interactive coding interviews with AI
- [ ] **Coding Assessments** - Automated coding challenges and grading
- [ ] **Learning Roadmaps** - Personalized learning paths
- [ ] **Advanced Analytics** - Deep dive performance analytics
- [ ] **Certificate Generation** - Auto-generated completion certificates
- [ ] **Email Notifications** - Automated email alerts and notifications
- [ ] **Docker Deployment** - Containerized deployment setup
- [ ] **Real-time Chat** - WebSocket-based real-time messaging
- [ ] **Slack/Discord Integration** - Platform notifications on chat apps
- [ ] **Mobile App** - Native mobile application

---

## 📦 Requirements

```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-jose==3.3.0
passlib==1.7.4
bcrypt==4.1.1
python-multipart==0.0.6
groq==0.4.1
python-dotenv==1.0.0
```

---

## 🚀 Deployment

### Local Development
```bash
uvicorn main:app --reload
```

### Production
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Upcoming)
```bash
docker build -t ezitech-portal .
docker run -p 8000:8000 ezitech-portal
```

---

## 📝 Environment Variables

```env
# API Configuration
GROQ_API_KEY=                    # Groq API Key
SECRET_KEY=                      # JWT Secret Key
ALGORITHM=HS256                  # JWT Algorithm

# Database
DATABASE_URL=sqlite:///./ezitech.db

# Server
DEBUG=True                       # Debug mode
HOST=127.0.0.1                  # Server host
PORT=8000                        # Server port

# Token
ACCESS_TOKEN_EXPIRE_MINUTES=30  # Token expiry time
```

---

## 📚 Documentation

### API Documentation
Visit `http://127.0.0.1:8000/docs` for interactive Swagger UI documentation.

### ReDoc
Visit `http://127.0.0.1:8000/redoc` for alternative API documentation.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 📞 Support & Contact

- **Issues**: Create an issue on GitHub
- **Email**: support@ezitech.com
- **Discord**: [Join our community](#)

---

## 🎉 Acknowledgments

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Groq API](https://groq.com/)
- [JWT Authentication](https://tools.ietf.org/html/rfc7519)

---

**Made with ❤️ by Ezitech Team**

Last Updated: July 2024
