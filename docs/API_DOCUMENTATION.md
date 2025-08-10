# Job Board API Documentation

## Overview

The Job Board API is a comprehensive RESTful API built with Django REST Framework that provides functionality for job posting, job searching, user management, and application tracking. The API features JWT authentication, data encryption for sensitive information, and comprehensive filtering and search capabilities.

## Base URL
```
http://localhost:8000/api/
```

## Authentication

### JWT Token Authentication
The API uses JSON Web Tokens (JWT) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-access-token>
```

### Token Endpoints

#### Obtain Token Pair
**POST** `/api/token/`

Obtain access and refresh tokens for authentication.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access": "string",
  "refresh": "string",
  "user": {
    "id": 1,
    "username": "string",
    "email": "user@example.com",
    "full_name": "string",
    "is_admin": false
  }
}
```

#### Refresh Token
**POST** `/api/token/refresh/`

Refresh an access token using a refresh token.

**Request Body:**
```json
{
  "refresh": "string"
}
```

**Response:**
```json
{
  "access": "string"
}
```

---

## Authentication Endpoints

### User Registration
**POST** `/auth/register/`

Register a new user account.

**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "first_name": "string",
  "last_name": "string",
  "full_name": "string",
  "phone_number": "string",
  "address": "string"
}
```

**Response (Success):**
```json
{
  "message": "User registered successfully"
}
```

**Response (Error):**
```json
{
  "error": "Username already exists"
}
```

### User Login
**POST** `/auth/login/`

Authenticate user and receive access tokens.

**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "remember_me": false
}
```

**Response:**
```json
{
  "access": "string",
  "refresh": "string",
  "user": {
    "id": 1,
    "username": "string",
    "email": "user@example.com",
    "full_name": "string"
  },
  "remember_me": false,
  "expires_in": "1 hour"
}
```

### User Logout
**POST** `/auth/logout/`

Logout user and blacklist tokens.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Logged out successfully."
}
```

### Password Reset - Request
**POST** `/auth/forgot-password/`

Request a password reset by sending a 6-digit verification code to the user's email.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "Password reset code has been sent to your email",
  "email": "user@example.com",
  "token": "generated-token-string",
  "expires_in": "1 hour"
}
```

### Password Reset - Verify Code
**POST** `/auth/verify-reset-code/`

Verify the 6-digit code received via email.

**Request Body:**
```json
{
  "token": "token-from-forgot-password",
  "code": "123456"
}
```

**Response:**
```json
{
  "message": "Verification code is valid",
  "token": "token-string",
  "valid": true
}
```

### Password Reset - Confirm
**POST** `/auth/reset-password/`

Reset the password using the verified token and code.

**Request Body:**
```json
{
  "token": "token-from-forgot-password",
  "code": "123456",
  "new_password": "NewSecurePassword123",
  "confirm_password": "NewSecurePassword123"
}
```

**Response:**
```json
{
  "message": "Password has been reset successfully. You can now login with your new password.",
  "success": true
}
```

### Password Reset - Resend Code
**POST** `/auth/resend-reset-code/`

Resend a new verification code if the previous one expired.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "A new password reset code has been sent to your email",
  "email": "user@example.com",
  "token": "new-token-string",
  "expires_in": "1 hour"
}
```

---

## User Profile Management

### Get User Profiles
**GET** `/api/profiles/`

Retrieve a list of public user profiles.

**Query Parameters:**
- `experience_level`: Filter by experience level (`entry`, `mid`, `senior`, `expert`)
- `is_available_for_hire`: Filter by availability (`true`, `false`)
- `city`: Filter by city (case-insensitive contains)
- `country`: Filter by country (case-insensitive contains)
- `skills`: Filter by skills (case-insensitive contains)
- `salary_min`: Filter by minimum expected salary
- `salary_max`: Filter by maximum expected salary
- `search`: Search in username, bio, job title, company, skills, city
- `ordering`: Order by `created_at`, `updated_at`, `expected_salary_min`

**Response:**
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/profiles/?page=2",
  "previous": null,
  "results": [
    {
      "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "full_name": "John Doe",
        "date_joined": "2024-01-01T00:00:00Z"
      },
      "bio": "Experienced software developer...",
      "age": 28,
      "gender": "male",
      "city": "New York",
      "country": "USA",
      "job_title": "Senior Developer",
      "company": "Tech Corp",
      "experience_level": "senior",
      "expected_salary_min": "80000.00",
      "expected_salary_max": "120000.00",
      "skills_list": ["Python", "Django", "React"],
      "education": "Bachelor's in Computer Science",
      "certifications": "AWS Certified Solutions Architect",
      "profile_image_url": "http://localhost:8000/media/profiles/profile_1.jpg",
      "linkedin_url": "https://linkedin.com/in/johndoe",
      "github_url": "https://github.com/johndoe",
      "website_url": "https://johndoe.com",
      "is_available_for_hire": true
    }
  ]
}
```

### Get Current User's Profile
**GET** `/account/profiles/my_profile/`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "date_joined": "2024-01-01T00:00:00Z"
  },
  "bio": "Experienced software developer...",
  "bio_decrypted": "Experienced software developer...",
  "date_of_birth": "1995-05-15",
  "age": 28,
  "gender": "male",
  "phone_number": "encrypted_data",
  "phone_number_decrypted": "+1-555-123-4567",
  "address": "encrypted_data",
  "address_decrypted": "123 Main St, New York, NY",
  "city": "New York",
  "country": "USA",
  "postal_code": "10001",
  "job_title": "Senior Developer",
  "company": "Tech Corp",
  "experience_level": "senior",
  "expected_salary_min": "80000.00",
  "expected_salary_max": "120000.00",
  "skills": "Python, Django, React, Node.js",
  "skills_list": ["Python", "Django", "React", "Node.js"],
  "education": "Bachelor's in Computer Science",
  "certifications": "AWS Certified Solutions Architect",
  "profile_image": "/media/profiles/profile_1.jpg",
  "profile_image_url": "http://localhost:8000/media/profiles/profile_1.jpg",
  "resume": "/media/resumes/resume_1.pdf",
  "resume_url": "http://localhost:8000/media/resumes/resume_1.pdf",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "github_url": "https://github.com/johndoe",
  "website_url": "https://johndoe.com",
  "is_profile_public": true,
  "is_available_for_hire": true,
  "application_count": 5,
  "jobs_posted_count": 2,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

### Update Current User's Profile
**PUT/PATCH** `/account/profiles/my_profile/`

**Headers:** 
- `Authorization: Bearer <token>`
- `Content-Type: application/json` or `multipart/form-data` (for file uploads)

**Request Body:**
```json
{
  "bio": "Updated bio...",
  "date_of_birth": "1995-05-15",
  "gender": "male",
  "phone_number": "+1-555-123-4567",
  "address": "123 Main St, New York, NY",
  "city": "New York",
  "country": "USA",
  "postal_code": "10001",
  "job_title": "Senior Developer",
  "company": "Tech Corp",
  "experience_level": "senior",
  "expected_salary_min": "80000.00",
  "expected_salary_max": "120000.00",
  "skills": "Python, Django, React, Node.js",
  "education": "Bachelor's in Computer Science",
  "certifications": "AWS Certified Solutions Architect",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "github_url": "https://github.com/johndoe",
  "website_url": "https://johndoe.com",
  "is_profile_public": true,
  "is_available_for_hire": true
}
```

### Upload Profile Image
**POST** `/api/profiles/{id}/upload_profile_image/`

**Headers:** 
- `Authorization: Bearer <token>`
- `Content-Type: multipart/form-data`

**Request Body (Form Data):**
- `profile_image`: Image file (JPEG, PNG, max 5MB)

**Response:**
```json
{
  "message": "Profile image updated successfully",
  "profile_image_url": "http://localhost:8000/media/profiles/profile_1.jpg"
}
```

### Upload Resume
**POST** `/api/profiles/{id}/upload_resume/`

**Headers:** 
- `Authorization: Bearer <token>`
- `Content-Type: multipart/form-data`

**Request Body (Form Data):**
- `resume`: File (PDF, DOC, DOCX, max 10MB)

**Response:**
```json
{
  "message": "Resume updated successfully"
}
```

### Get User Statistics
**GET** `/account/profiles/my_stats/`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "total_applications": 5,
  "pending_applications": 2,
  "successful_applications": 1,
  "total_jobs_posted": 2,
  "active_jobs_posted": 1,
  "profile_completion_percentage": 85
}
```

### Get Available Candidates
**GET** `/api/profiles/available_candidates/`

Get profiles of users available for hire.

**Query Parameters:** Same as profile listing

**Response:** Same structure as profile listing

### Update Account Information
**PUT/PATCH** `/account/profiles/update_account/`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "current_password": "currentpassword",
  "new_password": "newpassword123",
  "confirm_password": "newpassword123"
}
```

**Response:**
```json
{
  "message": "Account updated successfully"
}
```

---

## Job Management

### List Jobs
**GET** `/api/jobs/`

Retrieve a list of active job postings.

**Query Parameters:**
- `salary_min`: Filter by minimum salary
- `salary_max`: Filter by maximum salary
- `location`: Filter by location (case-insensitive contains)
- `company`: Filter by company name (case-insensitive contains)
- `employment_type`: Filter by employment type (`full_time`, `part_time`, `contract`, `internship`, `remote`)
- `experience_level`: Filter by experience level (`entry`, `mid`, `senior`, `executive`)
- `category`: Filter by category ID
- `search`: Search in title, description, company name, location, requirements
- `ordering`: Order by `created_at`, `application_deadline`, `salary_min`, `salary_max`

**Response:**
```json
{
  "count": 20,
  "next": "http://localhost:8000/api/jobs/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Senior Python Developer",
      "description": "We are looking for an experienced Python developer...",
      "company_name": "Tech Corp",
      "location": "New York, NY",
      "employment_type": "full_time",
      "experience_level": "senior",
      "salary_min": "80000.00",
      "salary_max": "120000.00",
      "category": {
        "id": 1,
        "name": "Software Development",
        "description": "Software development jobs"
      },
      "posted_by": {
        "id": 2,
        "username": "employer1",
        "full_name": "Jane Smith"
      },
      "application_deadline": "2024-02-15T23:59:59Z",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "application_count": 15
    }
  ]
}
```

### Get Job Details
**GET** `/api/jobs/{id}/`

**Response:**
```json
{
  "id": 1,
  "title": "Senior Python Developer",
  "description": "We are looking for an experienced Python developer...",
  "requirements": "- 5+ years Python experience\n- Django expertise\n- AWS knowledge",
  "responsibilities": "- Develop web applications\n- Code review\n- Mentoring junior developers",
  "benefits": "- Health insurance\n- 401k matching\n- Remote work options",
  "company_name": "Tech Corp",
  "company_description": "Leading technology company...",
  "location": "New York, NY",
  "employment_type": "full_time",
  "experience_level": "senior",
  "salary_min": "80000.00",
  "salary_max": "120000.00",
  "category": {
    "id": 1,
    "name": "Software Development",
    "description": "Software development jobs"
  },
  "posted_by": {
    "id": 2,
    "username": "employer1",
    "full_name": "Jane Smith"
  },
  "application_deadline": "2024-02-15T23:59:59Z",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "application_count": 15
}
```

### Create Job
**POST** `/api/jobs/`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "Senior Python Developer",
  "description": "We are looking for an experienced Python developer...",
  "requirements": "- 5+ years Python experience\n- Django expertise",
  "responsibilities": "- Develop web applications\n- Code review",
  "benefits": "- Health insurance\n- 401k matching",
  "company_name": "Tech Corp",
  "company_description": "Leading technology company...",
  "location": "New York, NY",
  "employment_type": "full_time",
  "experience_level": "senior",
  "salary_min": "80000.00",
  "salary_max": "120000.00",
  "category": 1,
  "application_deadline": "2024-02-15T23:59:59Z"
}
```

**Response:** Job details (same as GET job details)

### Update Job
**PUT/PATCH** `/api/jobs/{id}/`

**Headers:** `Authorization: Bearer <token>`

**Note:** Only the job owner can update their job postings.

**Request Body:** Same as create job

### Delete Job
**DELETE** `/api/jobs/{id}/`

**Headers:** `Authorization: Bearer <token>`

**Note:** Only the job owner can delete their job postings.

**Response:**
```json
{
  "message": "Job deleted successfully"
}
```

### Get My Jobs
**GET** `/api/jobs/my_jobs/`

Get jobs posted by the current user.

**Headers:** `Authorization: Bearer <token>`

**Response:** List of jobs (including inactive ones)

### Get Job Applications
**GET** `/api/jobs/{id}/applications/`

Get all applications for a specific job (only for job owner).

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": 1,
    "job": {
      "id": 1,
      "title": "Senior Python Developer"
    },
    "applicant": {
      "id": 3,
      "username": "applicant1",
      "full_name": "Mike Johnson"
    },
    "cover_letter": "I am very interested in this position...",
    "status": "pending",
    "applied_at": "2024-01-02T10:00:00Z",
    "updated_at": "2024-01-02T10:00:00Z"
  }
]
```

### Get Featured Jobs
**GET** `/api/jobs/featured/`

Get featured jobs (most applied to or recent).

**Response:** List of top 10 featured jobs

### Get Job Statistics
**GET** `/api/jobs/stats/`

**Response:**
```json
{
  "total_jobs": 100,
  "total_applications": 500,
  "employment_type_distribution": [
    {"employment_type": "full_time", "count": 60},
    {"employment_type": "part_time", "count": 20},
    {"employment_type": "contract", "count": 15},
    {"employment_type": "remote", "count": 5}
  ],
  "average_salary_by_level": [
    {"experience_level": "entry", "avg_salary": 45000.00},
    {"experience_level": "mid", "avg_salary": 70000.00},
    {"experience_level": "senior", "avg_salary": 95000.00}
  ]
}
```

---

## Application Management

### List Applications
**GET** `/api/applications/`

Get applications made by the current user.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `status`: Filter by status (`pending`, `reviewed`, `shortlisted`, `rejected`, `hired`)
- `job_title`: Filter by job title (case-insensitive contains)
- `company`: Filter by company name (case-insensitive contains)
- `search`: Search in job title, company name, cover letter
- `ordering`: Order by `applied_at`, `updated_at`, `status`

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "job": {
        "id": 1,
        "title": "Senior Python Developer",
        "company_name": "Tech Corp",
        "location": "New York, NY"
      },
      "applicant": {
        "id": 3,
        "username": "applicant1",
        "full_name": "Mike Johnson"
      },
      "cover_letter": "I am very interested in this position...",
      "status": "pending",
      "applied_at": "2024-01-02T10:00:00Z",
      "updated_at": "2024-01-02T10:00:00Z"
    }
  ]
}
```

### Get Application Details
**GET** `/api/applications/{id}/`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "job": {
    "id": 1,
    "title": "Senior Python Developer",
    "company_name": "Tech Corp",
    "location": "New York, NY",
    "employment_type": "full_time",
    "salary_min": "80000.00",
    "salary_max": "120000.00"
  },
  "applicant": {
    "id": 3,
    "username": "applicant1",
    "full_name": "Mike Johnson",
    "email": "mike@example.com"
  },
  "cover_letter": "I am very interested in this position...",
  "status": "pending",
  "applied_at": "2024-01-02T10:00:00Z",
  "updated_at": "2024-01-02T10:00:00Z"
}
```

### Create Application
**POST** `/api/applications/`

Apply for a job.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "job_id": 1,
  "cover_letter": "I am very interested in this position and believe I would be a great fit..."
}
```

**Response:** Application details

### Update Application Status
**PATCH** `/api/applications/{id}/update_status/`

Update application status (only for job owners).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "status": "shortlisted"
}
```

**Response:** Updated application details

### Withdraw Application
**DELETE** `/api/applications/{id}/`

Withdraw an application (only for applicants).

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Application withdrawn successfully"
}
```

### Get My Applications
**GET** `/api/applications/my_applications/`

Get all applications made by the current user.

**Headers:** `Authorization: Bearer <token>`

**Response:** List of user's applications

### Get Received Applications
**GET** `/api/applications/received_applications/`

Get all applications received for jobs posted by the current user.

**Headers:** `Authorization: Bearer <token>`

**Response:** List of applications to user's jobs

### Get Application Statistics
**GET** `/api/applications/stats/`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "total_applications": 5,
  "status_breakdown": {
    "pending": 2,
    "reviewed": 1,
    "shortlisted": 1,
    "rejected": 1,
    "hired": 0
  },
  "recent_applications": 3
}
```

---

## Category Management

### List Categories
**GET** `/api/categories/`

**Query Parameters:**
- `search`: Search in name and description
- `ordering`: Order by `name`, `created_at`

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Software Development",
      "description": "Software development and programming jobs",
      "is_active": true,
      "job_count": 25,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Get Category Details
**GET** `/api/categories/{id}/`

**Response:**
```json
{
  "id": 1,
  "name": "Software Development",
  "description": "Software development and programming jobs",
  "is_active": true,
  "job_count": 25,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Create Category
**POST** `/api/categories/`

**Headers:** `Authorization: Bearer <token>`

**Note:** Only admin users can create categories.

**Request Body:**
```json
{
  "name": "Data Science",
  "description": "Data science and analytics jobs"
}
```

### Update Category
**PUT/PATCH** `/api/categories/{id}/`

**Headers:** `Authorization: Bearer <token>`

**Note:** Only admin users can update categories.

### Delete Category
**DELETE** `/api/categories/{id}/`

**Headers:** `Authorization: Bearer <token>`

**Note:** Only admin users can delete categories.

### Get Category Jobs
**GET** `/api/categories/{id}/jobs/`

Get all active jobs in a specific category.

**Response:** List of jobs

### Get Category Statistics
**GET** `/api/categories/stats/`

**Response:**
```json
[
  {
    "id": 1,
    "name": "Software Development",
    "job_count": 25
  },
  {
    "id": 2,
    "name": "Data Science",
    "job_count": 12
  }
]
```

---

## Error Handling

The API uses standard HTTP status codes and returns error responses in JSON format:

### Common Error Responses

**400 Bad Request:**
```json
{
  "error": "Invalid request data",
  "details": {
    "field_name": ["This field is required."]
  }
}
```

**401 Unauthorized:**
```json
{
  "error": "Authentication credentials were not provided."
}
```

**403 Forbidden:**
```json
{
  "error": "You do not have permission to perform this action."
}
```

**404 Not Found:**
```json
{
  "error": "Not found."
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error. Please try again later."
}
```

---

## Rate Limiting

The API implements rate limiting to prevent abuse:
- **Anonymous users:** 100 requests per hour
- **Authenticated users:** 1000 requests per hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

---

## Pagination

List endpoints support pagination using page numbers:

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Number of items per page (default: 20, max: 100)

**Response Format:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/jobs/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Data Encryption

Sensitive user data is automatically encrypted using AES-256 encryption:
- Phone numbers
- Addresses
- Bio information
- Personal information in user profiles

The API automatically handles encryption/decryption, and returns both encrypted and decrypted versions of sensitive fields where appropriate.

---

## File Uploads

### Supported File Types

**Profile Images:**
- JPEG, PNG
- Maximum size: 5MB
- Automatically resized to 500x500px

**Resumes:**
- PDF, DOC, DOCX
- Maximum size: 10MB

### Upload Process

Use `multipart/form-data` content type for file uploads:

```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -F "profile_image=@profile.jpg" \
  http://localhost:8000/api/profiles/1/upload_profile_image/
```

---

## Interactive API Documentation

The API provides interactive documentation:
- **Swagger UI:** `http://localhost:8000/swagger/`
- **ReDoc:** `http://localhost:8000/redoc/`
- **JSON Schema:** `http://localhost:8000/swagger.json`

---

## Examples

### Complete Job Application Flow

1. **Register User:**
```bash
curl -X POST http://localhost:8000/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jobseeker",
    "password": "SecurePass123",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone_number": "+1-555-123-4567"
  }'
```

2. **Login:**
```bash
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jobseeker",
    "password": "SecurePass123"
  }'
```

3. **Update Profile:**
```bash
curl -X PATCH http://localhost:8000/account/profiles/my_profile/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "Experienced software developer",
    "job_title": "Senior Developer",
    "skills": "Python, Django, React"
  }'
```

4. **Search Jobs:**
```bash
curl "http://localhost:8000/api/jobs/?search=python&employment_type=full_time"
```

5. **Apply for Job:**
```bash
curl -X POST http://localhost:8000/api/applications/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 1,
    "cover_letter": "I am very interested in this Python developer position..."
  }'
```

### Employer Workflow

1. **Create Job Posting:**
```bash
curl -X POST http://localhost:8000/api/jobs/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "description": "Looking for experienced Python developer...",
    "company_name": "Tech Corp",
    "location": "New York, NY",
    "employment_type": "full_time",
    "experience_level": "senior",
    "salary_min": "80000",
    "salary_max": "120000",
    "category": 1
  }'
```

2. **View Applications:**
```bash
curl http://localhost:8000/api/jobs/1/applications/ \
  -H "Authorization: Bearer <token>"
```

3. **Update Application Status:**
```bash
curl -X PATCH http://localhost:8000/api/applications/1/update_status/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "shortlisted"}'
```

---

## Support

For API support and questions:
- Email: brahim.chatri.dev@gmail.com
- Documentation: Available at `/swagger/` and `/redoc/` endpoints
- GitHub Issues: Submit issues to the project repository
