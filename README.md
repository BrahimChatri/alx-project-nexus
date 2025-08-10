
# 📚 ALX Project Nexus – Job Board Platform Backend

Welcome to my `alx-project-nexus` repository! This project serves as a comprehensive documentation hub for my journey through the **ProDev Backend Engineering Program**. It reflects the knowledge, tools, challenges, and best practices I’ve acquired, and showcases my final capstone project: **Job Board Platform Backend**.

---

## 🚀 Capstone Project: Job Board Platform Backend

The goal of this backend project is to build a fully functional, scalable API that powers a job board platform. The system allows companies to post jobs and job seekers to apply — using Django and Django REST Framework.

---

## 🎯 Objectives

- Consolidate backend engineering concepts and skills learned throughout the program.
- Build a real-world backend application with RESTful API endpoints.
- Apply best practices in design, development, and documentation.
- Collaborate with frontend learners for API integration and testing.

---

## 🧠 Key Learnings & Technologies

### 🔧 Technologies Used
- **Python 3**
- **Django**
- **Django REST Framework (DRF)**
- **PostgreSQL**
- **Docker & Docker Compose**
- **Celery + RabbitMQ** (for background task processing)
- **Swagger / drf-yasg** (for API documentation)
- **Git & GitHub**
- **CI/CD with GitHub Actions**

---

## 🧩 Backend Concepts Covered

- RESTful API design and implementation
- Authentication and permission management
- Database modeling and relational design
- Filtering, searching, and pagination
- Asynchronous processing (email notifications, background tasks)
- API documentation and testing
- Secure coding practices (input validation, JWT)
- Version control and Git collaboration
- Containerization and deployment

---

## 📦 Core Features of the Job Board Platform

### 🔐 **Authentication System**
- Custom user model with encrypted personal data
- JWT-based authentication (login, logout, register)
- **Password Reset with Email Verification** - 6-digit codes sent via email
- Password strength validation with comprehensive rules
- Secure token refresh mechanism with blacklisting
- Remember Me functionality with extended token lifetime
- Token rotation and automatic invalidation

### 👤 **User Profile Management**
- Comprehensive user profiles with personal and professional information
- Profile image and resume upload capabilities
- Privacy settings for profile visibility
- Skills, education, and certification tracking
- Social media links integration

### 📂 **Categories Management**
- CRUD operations for job categories
- Admin-only category creation
- Category statistics and job counts
- Search and filtering capabilities

### 💼 **Job Management**
- Complete job posting system with rich details
- Advanced filtering by employment type, experience level, salary range
- Location-based and company-based filtering
- Featured jobs system
- User-specific job management
- Job statistics and analytics

### 📄 **Applications System**
- Job application submission with resume upload
- Application status tracking (pending, reviewed, shortlisted, rejected, hired)
- Duplicate application prevention
- Separate views for applicants and employers
- Application statistics and reporting

### 📊 **Statistics & Analytics**
- Job posting statistics
- Application tracking metrics
- User profile analytics
- Category-wise job distribution

### 📄 **API Documentation**
- Interactive Swagger/OpenAPI documentation
- Complete endpoint documentation with examples
- ReDoc alternative documentation

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL (or use SQLite for development)
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/BrahimChatri/alx-project-nexus.git
   cd alx-project-nexus
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Set up database:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Populate sample data:**
   ```bash
   python manage.py populate_data
   ```

7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

### 🌐 Access Points
- **API Base URL:** http://127.0.0.1:8000/
- **Interactive API Docs:** http://127.0.0.1:8000/swagger/
- **Alternative Docs:** http://127.0.0.1:8000/redoc/
- **Admin Panel:** http://127.0.0.1:8000/admin/

### 📁 Folder Structure
```
📦 
├─ .dockerignore
├─ .github
│  └─ workflows
│     └─ ci.yml
├─ .gitignore
├─ Dockerfile
├─ README.md
├─ backend
│  ├─ apps
│  │  ├─ applications
│  │  │  ├─ __init__.py
│  │  │  ├─ admin.py
│  │  │  ├─ apps.py
│  │  │  ├─ migrations
│  │  │  │  ├─ 0001_initial.py
│  │  │  │  └─ __init__.py
│  │  │  ├─ models.py
│  │  │  ├─ serializers.py
│  │  │  ├─ tests.py
│  │  │  ├─ urls.py
│  │  │  └─ views.py
│  │  ├─ authentication
│  │  │  ├─ __init__.py
│  │  │  ├─ admin.py
│  │  │  ├─ apps.py
│  │  │  ├─ email_utils.py
│  │  │  ├─ migrations
│  │  │  │  ├─ 0001_initial.py
│  │  │  │  ├─ 0002_alter_customuser_options_alter_customuser_address_and_more.py
│  │  │  │  ├─ 0003_alter_customuser_first_name_and_more.py
│  │  │  │  ├─ 0004_passwordresettoken.py
│  │  │  │  └─ __init__.py
│  │  │  ├─ models.py
│  │  │  ├─ serializers.py
│  │  │  ├─ tests.py
│  │  │  ├─ urls.py
│  │  │  └─ views.py
│  │  ├─ categories
│  │  │  ├─ __init__.py
│  │  │  ├─ admin.py
│  │  │  ├─ apps.py
│  │  │  ├─ management
│  │  │  │  ├─ __init__.py
│  │  │  │  └─ commands
│  │  │  │     ├─ __init__.py
│  │  │  │     └─ populate_data.py
│  │  │  ├─ migrations
│  │  │  │  ├─ 0001_initial.py
│  │  │  │  └─ __init__.py
│  │  │  ├─ models.py
│  │  │  ├─ serializers.py
│  │  │  ├─ tests.py
│  │  │  ├─ urls.py
│  │  │  └─ views.py
│  │  ├─ jobs
│  │  │  ├─ __init__.py
│  │  │  ├─ admin.py
│  │  │  ├─ apps.py
│  │  │  ├─ migrations
│  │  │  │  ├─ 0001_initial.py
│  │  │  │  └─ __init__.py
│  │  │  ├─ models.py
│  │  │  ├─ serializers.py
│  │  │  ├─ tests.py
│  │  │  ├─ urls.py
│  │  │  └─ views.py
│  │  └─ users
│  │     ├─ __init__.py
│  │     ├─ admin.py
│  │     ├─ apps.py
│  │     ├─ management
│  │     │  └─ commands
│  │     │     └─ test_encryption.py
│  │     ├─ migrations
│  │     │  ├─ 0001_initial.py
│  │     │  ├─ 0002_alter_userprofile_gender_and_more.py
│  │     │  ├─ 0003_increase_encrypted_field_lengths.py
│  │     │  └─ __init__.py
│  │     ├─ models.py
│  │     ├─ serializers.py
│  │     ├─ tests.py
│  │     ├─ urls.py
│  │     └─ views.py
│  ├─ entrypoint.sh
│  ├─ example.env
│  ├─ job_board
│  │  ├─ __init__.py
│  │  ├─ asgi.py
│  │  ├─ settings.py
│  │  ├─ urls.py
│  │  └─ wsgi.py
│  ├─ manage.py
│  ├─ requirements.txt
│  └─ utils
│     ├─ README_ENCRYPTION.md
│     ├─ __init__.py
│     └─ encryption.py
├─ docs
│  ├─ API_DOCUMENTATION.md
│  ├─ GETTING_STARTED.md
│  ├─ PASSWORD_RESET_README.md
│  ├─ README.md
│  ├─ TESTING_GUIDE.md
│  ├─ diagram.pdf
│  ├─ diagram.png
│  └─ representation.md
└─ tests
   ├─ load_data.py
   ├─ test_api.py
   ├─ test_media_upload.py
   └─ test_remember_me.py
```

### 📝 API Documentation
Detailed API documentation is available in the `/docs/` directory:
- [`GETTING_STARTED.md`](./docs/GETTING_STARTED.md) - Complete setup guide with Docker
- [`API_DOCUMENTATION.md`](./docs/API_DOCUMENTATION.md) - Complete API reference with examples
- [`PASSWORD_RESET_README.md`](./docs/PASSWORD_RESET_README.md) - Password reset functionality guide
- [`TESTING_GUIDE.md`](./docs/TESTING_GUIDE.md) - Comprehensive testing instructions
- [`representation.md`](./docs/representation.md) - Comprehensive project presentation

### 🔗 Quick Access Links
- **Interactive API Docs:** http://127.0.0.1:8000/swagger/
- **Alternative Docs:** http://127.0.0.1:8000/redoc/
- **Admin Panel:** http://127.0.0.1:8000/admin/

## 🔌 API Endpoints Overview

### Authentication
```
POST /auth/register/              # User registration
POST /auth/login/                 # User login (with remember me)
POST /auth/logout/                # User logout
POST /auth/forgot-password/       # Request password reset
POST /auth/verify-reset-code/     # Verify 6-digit code
POST /auth/reset-password/        # Confirm password reset
POST /auth/resend-reset-code/     # Resend verification code
POST /api/token/                  # Get JWT tokens
POST /api/token/refresh/          # Refresh JWT token
```

### User Profiles
```
GET    /api/profiles/                        # List public profiles
GET    /api/profiles/available_candidates/   # Available candidates
GET    /account/profiles/my_profile/         # Get current user profile
PATCH  /account/profiles/my_profile/         # Update profile
GET    /account/profiles/my_stats/           # User statistics
POST   /api/profiles/{id}/upload_profile_image/  # Upload profile image
POST   /api/profiles/{id}/upload_resume/         # Upload resume
```

### Job Management
```
GET    /api/jobs/                    # List jobs with filtering
POST   /api/jobs/                    # Create job posting
GET    /api/jobs/{id}/               # Get job details
PATCH  /api/jobs/{id}/               # Update job
DELETE /api/jobs/{id}/               # Delete job
GET    /api/jobs/my_jobs/            # User's posted jobs
GET    /api/jobs/featured/           # Featured jobs
GET    /api/jobs/stats/              # Job statistics
GET    /api/jobs/{id}/applications/  # Job applications (employer view)
```

### Application Management
```
GET    /api/applications/                     # List user applications
POST   /api/applications/                     # Apply to job
GET    /api/applications/{id}/                # Application details
DELETE /api/applications/{id}/                # Withdraw application
PATCH  /api/applications/{id}/update_status/  # Update status (employers)
GET    /api/applications/my_applications/     # My applications
GET    /api/applications/received_applications/ # Received applications
GET    /api/applications/stats/               # Application statistics
```

### Categories
```
GET    /api/categories/              # List categories
POST   /api/categories/              # Create category (admin)
GET    /api/categories/{id}/         # Category details
PATCH  /api/categories/{id}/         # Update category (admin)
DELETE /api/categories/{id}/         # Delete category (admin)
GET    /api/categories/{id}/jobs/    # Jobs in category
GET    /api/categories/stats/        # Category statistics
```

### Documentation
```
GET    /swagger/                     # Interactive API documentation
GET    /redoc/                       # Alternative documentation
GET    /swagger.json                 # OpenAPI JSON schema
GET    /admin/                       # Django admin panel
```

---

## 🧪 Testing

### Comprehensive Test Suite
- **15 Test Categories** covering all functionality
- **Faker Integration** for realistic random test data
- **Performance Testing** with load testing capabilities
- **Security Testing** for permissions and validation
- **Automated Test Runner** with detailed reporting

### Test Coverage
- **Authentication System**: Registration, login, logout, password reset, JWT tokens
- **User Profiles**: Profile management, file uploads, encryption verification
- **Job Management**: CRUD operations, filtering, search, statistics
- **Application System**: Application lifecycle, status tracking, permissions
- **Security**: Access control, data validation, error handling
- **Performance**: Load testing, pagination, concurrent requests

### Run Tests
```bash
# Run comprehensive test suite
cd backend
python full_test.py

# Run specific Django tests
python manage.py test

# Run with coverage
python manage.py test --verbosity=2
```

### Test Documentation
- [`TESTING_GUIDE.md`](./docs/TESTING_GUIDE.md) - Complete testing instructions
- [`full_test.py`](./backend/full_test.py) - Automated test suite

---

## 🐳 Docker & CI/CD
- Dockerized backend and PostgreSQL services
- GitHub Actions to automate testing on push and pull requests

---

## ✅ Best Practices Followed

- Modular project structure (separate apps for clarity)
- Use of environment variables for secrets
- Input validation and permission checks
- DRY principles and reusable serializers/views
- Clean commit history and Git branching

---

## 📹 Project Deliverables

- 🔗 [GitHub Repository](https://github.com/your-username/alx-project-nexus)
- 🎥 Video Demo (link here)
- 🖼️ Presentation Slides (link here)
- 📘 API Documentation (Swagger or Postman collection)

---

## 🤝 Collaboration

This project supports frontend-backend collaboration through:
- Shared API specs
- Swagger docs for testing endpoints
- Active communication on Discord

---
## ‍💻 Author

**Brahim Chatri** - ALX ProDev Backend Student

- 📧 Email: [brahim.chatri.dev@gmail.com](mailto:brahim.chatri.dev@gmail.com)
- 🔗 LinkedIn: [linkedin.com/in/brahim-chatri](www.linkedin.com/in/brahim-chatri)
- 🐙 GitHub: [BrahimChatri](https://github.com/BrahimChatri)


## 💬 Let's Connect

I'm always open to feedback, discussion, and collaboration. Feel free to raise issues or suggestions.

> *"Backend is the engine of innovation. Build it right, scale it strong."*


