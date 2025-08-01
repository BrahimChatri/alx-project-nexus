# Job Board API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
This API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-token-here>
```

## Endpoints

### Authentication

#### Register User
- **POST** `/auth/register/`
- **Body:**
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

#### Login
- **POST** `/auth/login/`
- **Body:**
```json
{
  "username": "string",
  "password": "string"
}
```
- **Response:**
```json
{
  "access": "jwt-token"
}
```

#### Logout
- **POST** `/auth/logout/`
- **Headers:** `Authorization: Bearer <token>`

### Categories

#### List Categories
- **GET** `/api/categories/`
- **Query Parameters:**
  - `search`: Search by name or description
  - `ordering`: Order by `name` or `created_at`

#### Get Category Details
- **GET** `/api/categories/{id}/`

#### Get Jobs in Category
- **GET** `/api/categories/{id}/jobs/`

#### Category Statistics
- **GET** `/api/categories/stats/`

#### Create Category (Admin only)
- **POST** `/api/categories/`
- **Headers:** `Authorization: Bearer <admin-token>`
- **Body:**
```json
{
  "name": "string",
  "description": "string",
  "is_active": true
}
```

### Jobs

#### List Jobs
- **GET** `/api/jobs/`
- **Query Parameters:**
  - `search`: Search in title, description, company, location
  - `employment_type`: `full_time`, `part_time`, `contract`, `internship`, `remote`
  - `experience_level`: `entry`, `mid`, `senior`, `executive`
  - `category`: Category ID
  - `location`: Filter by location (contains)
  - `company`: Filter by company name (contains)
  - `salary_min`: Minimum salary
  - `salary_max`: Maximum salary
  - `ordering`: Order by `created_at`, `salary_min`, `salary_max`, `application_deadline`

#### Get Job Details
- **GET** `/api/jobs/{id}/`

#### Create Job
- **POST** `/api/jobs/`
- **Headers:** `Authorization: Bearer <token>`
- **Body:**
```json
{
  "title": "string",
  "description": "string",
  "company_name": "string",
  "location": "string",
  "employment_type": "full_time",
  "experience_level": "entry",
  "salary_min": 50000,
  "salary_max": 80000,
  "requirements": "string",
  "benefits": "string",
  "category_id": 1,
  "application_deadline": "2024-12-31T23:59:59Z"
}
```

#### Update Job
- **PUT/PATCH** `/api/jobs/{id}/`
- **Headers:** `Authorization: Bearer <token>`
- **Note:** Only job owner can update

#### Delete Job
- **DELETE** `/api/jobs/{id}/`
- **Headers:** `Authorization: Bearer <token>`
- **Note:** Only job owner can delete

#### My Jobs
- **GET** `/api/jobs/my_jobs/`
- **Headers:** `Authorization: Bearer <token>`

#### Job Applications (for job owner)
- **GET** `/api/jobs/{id}/applications/`
- **Headers:** `Authorization: Bearer <token>`

#### Featured Jobs
- **GET** `/api/jobs/featured/`

#### Job Statistics
- **GET** `/api/jobs/stats/`

### Applications

#### List My Applications
- **GET** `/api/applications/my_applications/`
- **Headers:** `Authorization: Bearer <token>`

#### Get Application Details
- **GET** `/api/applications/{id}/`
- **Headers:** `Authorization: Bearer <token>`

#### Apply to Job
- **POST** `/api/applications/`
- **Headers:** `Authorization: Bearer <token>`
- **Body:**
```json
{
  "job_id": 1,
  "cover_letter": "string",
  "resume": "file"
}
```

#### Withdraw Application
- **DELETE** `/api/applications/{id}/`
- **Headers:** `Authorization: Bearer <token>`
- **Note:** Only applicant can withdraw

#### Received Applications (for job owners)
- **GET** `/api/applications/received_applications/`
- **Headers:** `Authorization: Bearer <token>`

#### Update Application Status (job owners only)
- **PATCH** `/api/applications/{id}/update_status/`
- **Headers:** `Authorization: Bearer <token>`
- **Body:**
```json
{
  "status": "reviewed"
}
```
- **Status options:** `pending`, `reviewed`, `shortlisted`, `rejected`, `hired`

#### Application Statistics
- **GET** `/api/applications/stats/`
- **Headers:** `Authorization: Bearer <token>`

## Response Format

### Success Response
```json
{
  "count": 20,
  "next": "http://localhost:8000/api/jobs/?page=2",
  "previous": null,
  "results": [...]
}
```

### Error Response
```json
{
  "error": "Error message",
  "detail": "Detailed error description"
}
```

## Status Codes
- `200 OK`: Success
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Interactive Documentation
Visit `/swagger/` or `/redoc/` for interactive API documentation.
