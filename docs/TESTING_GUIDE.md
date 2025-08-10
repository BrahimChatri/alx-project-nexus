# Complete Testing Guide - ALX Project Nexus Job Board Platform

## 🎯 Overview

This guide provides comprehensive testing instructions for the ALX Project Nexus Job Board Platform, covering all API endpoints, security features, and functionality with realistic test data.

---

## 🚀 Quick Test Setup

### 1. Run the Comprehensive Test Suite

The project includes a complete test suite that tests all endpoints with Faker-generated random data:

```bash
# Navigate to backend directory
cd backend

# Run the comprehensive test suite
python full_test.py

# Or run with Django's test runner
python manage.py test backend.full_test
```

### 2. Interactive API Testing

Access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/
- **Admin Panel**: http://localhost:8000/admin/

---

## 📋 Manual Testing Checklist

### ✅ Authentication System Testing

#### User Registration
```bash
curl -X POST http://localhost:8000/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser123",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone_number": "+1-555-123-4567",
    "address": "123 Main St, New York, NY"
  }'
```

#### User Login (Standard)
```bash
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser123",
    "password": "SecurePass123!"
  }'
```

#### User Login (Remember Me)
```bash
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser123",
    "password": "SecurePass123!",
    "remember_me": true
  }'
```

#### Password Reset Flow
```bash
# Step 1: Request password reset
curl -X POST http://localhost:8000/auth/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# Step 2: Verify 6-digit code (check email)
curl -X POST http://localhost:8000/auth/verify-reset-code/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "token-from-step-1",
    "code": "123456"
  }'

# Step 3: Reset password
curl -X POST http://localhost:8000/auth/reset-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "token-from-step-1",
    "code": "123456",
    "new_password": "NewSecurePass123!",
    "confirm_password": "NewSecurePass123!"
  }'

# Step 4: Resend code if needed
curl -X POST http://localhost:8000/auth/resend-reset-code/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

#### JWT Token Management
```bash
# Get JWT tokens
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser123",
    "password": "SecurePass123!"
  }'

# Refresh token
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "your-refresh-token"}'

# Logout (blacklist token)
curl -X POST http://localhost:8000/auth/logout/ \
  -H "Authorization: Bearer your-access-token"
```

### ✅ User Profile Management Testing

#### Get My Profile
```bash
curl -X GET http://localhost:8000/account/profiles/my_profile/ \
  -H "Authorization: Bearer your-access-token"
```

#### Update Profile
```bash
curl -X PATCH http://localhost:8000/account/profiles/my_profile/ \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "Experienced software developer with 5+ years in Python and Django",
    "job_title": "Senior Backend Developer",
    "company": "Tech Innovations Inc",
    "experience_level": "senior",
    "skills": "Python, Django, PostgreSQL, Docker, AWS",
    "expected_salary_min": "85000",
    "expected_salary_max": "120000",
    "city": "San Francisco",
    "country": "USA",
    "is_available_for_hire": true,
    "linkedin_url": "https://linkedin.com/in/johndoe",
    "github_url": "https://github.com/johndoe"
  }'
```

#### Upload Profile Image
```bash
curl -X POST http://localhost:8000/api/profiles/1/upload_profile_image/ \
  -H "Authorization: Bearer your-access-token" \
  -F "profile_image=@profile.jpg"
```

#### Upload Resume
```bash
curl -X POST http://localhost:8000/api/profiles/1/upload_resume/ \
  -H "Authorization: Bearer your-access-token" \
  -F "resume=@resume.pdf"
```

#### Get User Statistics
```bash
curl -X GET http://localhost:8000/account/profiles/my_stats/ \
  -H "Authorization: Bearer your-access-token"
```

#### List Public Profiles
```bash
# All public profiles
curl "http://localhost:8000/api/profiles/"

# Available candidates only
curl "http://localhost:8000/api/profiles/available_candidates/"

# Filtered profiles
curl "http://localhost:8000/api/profiles/?experience_level=senior&is_available_for_hire=true&search=python"
```

### ✅ Job Management Testing

#### List Jobs with Filtering
```bash
# All jobs
curl "http://localhost:8000/api/jobs/"

# Filtered jobs
curl "http://localhost:8000/api/jobs/?employment_type=full_time&experience_level=senior&salary_min=80000"

# Search jobs
curl "http://localhost:8000/api/jobs/?search=python%20developer&location=New%20York"

# Jobs by category
curl "http://localhost:8000/api/jobs/?category=1"

# Featured jobs
curl "http://localhost:8000/api/jobs/featured/"
```

#### Create Job Posting
```bash
curl -X POST http://localhost:8000/api/jobs/ \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Full Stack Developer",
    "description": "We are looking for an experienced full stack developer to join our growing team. You will be responsible for developing and maintaining web applications using modern technologies.",
    "company_name": "TechStart Solutions",
    "location": "San Francisco, CA",
    "employment_type": "full_time",
    "experience_level": "senior",
    "salary_min": "95000",
    "salary_max": "140000",
    "requirements": "- 5+ years of full stack development experience\n- Proficiency in Python/Django and React\n- Experience with PostgreSQL and cloud platforms\n- Strong problem-solving skills",
    "benefits": "- Competitive salary and equity\n- Health, dental, and vision insurance\n- 401k matching\n- Remote work flexibility\n- Professional development budget",
    "category": 1,
    "application_deadline": "2024-03-15T23:59:59Z"
  }'
```

#### Update Job
```bash
curl -X PATCH http://localhost:8000/api/jobs/1/ \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Senior Full Stack Developer",
    "salary_max": "150000"
  }'
```

#### Get My Jobs
```bash
curl -X GET http://localhost:8000/api/jobs/my_jobs/ \
  -H "Authorization: Bearer your-access-token"
```

#### Get Job Applications (Employer View)
```bash
curl -X GET http://localhost:8000/api/jobs/1/applications/ \
  -H "Authorization: Bearer your-access-token"
```

#### Job Statistics
```bash
curl "http://localhost:8000/api/jobs/stats/"
```

### ✅ Application Management Testing

#### Create Application
```bash
curl -X POST http://localhost:8000/api/applications/ \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 1,
    "cover_letter": "Dear Hiring Manager,\n\nI am writing to express my strong interest in the Senior Full Stack Developer position at TechStart Solutions. With over 6 years of experience in full stack development and a proven track record of delivering high-quality web applications, I am confident I would be a valuable addition to your team.\n\nMy experience includes:\n- Building scalable web applications using Python/Django and React\n- Working with PostgreSQL and optimizing database performance\n- Deploying applications on AWS and managing cloud infrastructure\n- Leading development teams and mentoring junior developers\n\nI am particularly excited about this opportunity because of TechStart Solutions reputation for innovation and the chance to work on challenging technical problems. I am available for an interview at your convenience.\n\nThank you for considering my application.\n\nBest regards,\nJohn Doe"
  }'
```

#### List My Applications
```bash
curl -X GET http://localhost:8000/api/applications/ \
  -H "Authorization: Bearer your-access-token"

# With filtering
curl -X GET "http://localhost:8000/api/applications/?status=pending&search=developer" \
  -H "Authorization: Bearer your-access-token"
```

#### Get Application Details
```bash
curl -X GET http://localhost:8000/api/applications/1/ \
  -H "Authorization: Bearer your-access-token"
```

#### Update Application Status (Employer Only)
```bash
curl -X PATCH http://localhost:8000/api/applications/1/update_status/ \
  -H "Authorization: Bearer employer-access-token" \
  -H "Content-Type: application/json" \
  -d '{"status": "reviewed"}'

# Progress through status stages
curl -X PATCH http://localhost:8000/api/applications/1/update_status/ \
  -H "Authorization: Bearer employer-access-token" \
  -H "Content-Type: application/json" \
  -d '{"status": "shortlisted"}'
```

#### Withdraw Application
```bash
curl -X DELETE http://localhost:8000/api/applications/1/ \
  -H "Authorization: Bearer your-access-token"
```

#### Get Received Applications (Employer View)
```bash
curl -X GET http://localhost:8000/api/applications/received_applications/ \
  -H "Authorization: Bearer employer-access-token"
```

#### Application Statistics
```bash
curl -X GET http://localhost:8000/api/applications/stats/ \
  -H "Authorization: Bearer your-access-token"
```

### ✅ Category Management Testing

#### List Categories
```bash
# All categories
curl "http://localhost:8000/api/categories/"

# Search categories
curl "http://localhost:8000/api/categories/?search=software"

# Category statistics
curl "http://localhost:8000/api/categories/stats/"
```

#### Create Category (Admin Only)
```bash
curl -X POST http://localhost:8000/api/categories/ \
  -H "Authorization: Bearer admin-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Artificial Intelligence",
    "description": "AI and machine learning positions including data scientists, ML engineers, and AI researchers"
  }'
```

#### Get Category Details
```bash
curl "http://localhost:8000/api/categories/1/"
```

#### Get Jobs in Category
```bash
curl "http://localhost:8000/api/categories/1/jobs/"
```

---

## 🔒 Security Testing

### Permission Testing

#### Test Unauthorized Access
```bash
# Should return 401
curl -X GET http://localhost:8000/account/profiles/my_profile/

# Should return 401
curl -X GET http://localhost:8000/api/applications/
```

#### Test Forbidden Access
```bash
# Try to update someone else's job (should return 403/404)
curl -X PATCH http://localhost:8000/api/jobs/1/ \
  -H "Authorization: Bearer unauthorized-token" \
  -H "Content-Type: application/json" \
  -d '{"title": "Hacked Title"}'

# Try to create category as regular user (should return 403)
curl -X POST http://localhost:8000/api/categories/ \
  -H "Authorization: Bearer regular-user-token" \
  -H "Content-Type: application/json" \
  -d '{"name": "Unauthorized Category"}'
```

### Data Validation Testing

#### Test Invalid Data
```bash
# Invalid job data
curl -X POST http://localhost:8000/api/jobs/ \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "",
    "description": "",
    "salary_min": "invalid",
    "employment_type": "invalid_type"
  }'

# Invalid registration data
curl -X POST http://localhost:8000/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "",
    "password": "weak"
  }'
```

### File Upload Security Testing

#### Test Invalid File Types
```bash
# Try uploading text file as image
curl -X POST http://localhost:8000/api/profiles/1/upload_profile_image/ \
  -H "Authorization: Bearer your-access-token" \
  -F "profile_image=@malicious.txt"

# Try uploading executable as resume
curl -X POST http://localhost:8000/api/profiles/1/upload_resume/ \
  -H "Authorization: Bearer your-access-token" \
  -F "resume=@malicious.exe"
```

---

## 📊 Performance Testing

### Load Testing with Apache Bench

```bash
# Test job listing endpoint
ab -n 1000 -c 10 http://localhost:8000/api/jobs/

# Test with authentication
ab -n 500 -c 5 -H "Authorization: Bearer your-token" http://localhost:8000/api/applications/

# Test search functionality
ab -n 200 -c 5 "http://localhost:8000/api/jobs/?search=developer&employment_type=full_time"
```

### Pagination Testing

```bash
# Test pagination limits
curl "http://localhost:8000/api/jobs/?page=1&page_size=5"
curl "http://localhost:8000/api/jobs/?page=999"  # High page number
curl "http://localhost:8000/api/jobs/?page_size=100"  # Maximum page size
curl "http://localhost:8000/api/jobs/?page_size=1"  # Minimum page size
```

---

## 🧪 Automated Test Suite Details

The `full_test.py` file includes 15 comprehensive test categories:

### Test Categories Overview

1. **Authentication Endpoints** - Registration, login, logout, JWT tokens, password reset
2. **Category Endpoints** - CRUD operations, search, statistics
3. **User Profile Endpoints** - Profile management, file uploads, filtering
4. **Job Management Endpoints** - Job CRUD, filtering, search, statistics
5. **Application Endpoints** - Application lifecycle, status management
6. **Pagination & Search** - Advanced search and pagination testing
7. **Permissions & Security** - Access control and security measures
8. **Data Validation** - Input validation and error handling
9. **File Upload Validation** - File type and size validation
10. **Advanced Features** - Ordering, edge cases, complex queries
11. **Comprehensive Workflow** - End-to-end user journeys
12. **Stress Testing** - Performance and load testing
13. **API Documentation** - Documentation accessibility
14. **Data Encryption** - Encryption/decryption verification
15. **Error Handling** - Comprehensive error response testing

### Test Data Generated

The test suite uses Faker to generate realistic test data:

- **10 Test Users** with encrypted personal information
- **8 Job Categories** covering major industries
- **15 Job Postings** with realistic details and requirements
- **20 Applications** with various statuses
- **1 Admin User** for testing administrative functions

### Sample Test Output

```
================================================================================
🚀 ALX PROJECT NEXUS - COMPREHENSIVE API TEST SUITE
================================================================================
📊 Test Data Created:
   👥 Users: 11 (including admin)
   📂 Categories: 8
   💼 Jobs: 15
   📄 Applications: 20
================================================================================

🔐 Testing Authentication Endpoints...
   ✅ User Registration: 201
   ✅ User Login: 200
   ✅ Remember Me Login: 200
   ✅ JWT Token Obtain: 200
   ✅ JWT Token Refresh: 200
   ✅ User Logout: 200
   ✅ Forgot Password: 200

📂 Testing Category Endpoints...
   ✅ List Categories: 200 (8 categories)
   ✅ Category Details: 200
   ✅ Category Jobs: 200
   ✅ Category Statistics: 200
   ✅ Create Category (Admin): 201
   ✅ Category Search: 200

...

================================================================================
📋 COMPREHENSIVE TEST REPORT
================================================================================

📊 Database State After Testing:
   👥 Total Users: 11
   📝 Total Profiles: 11
   📂 Total Categories: 9
   💼 Total Jobs: 16
   📄 Applications: 21

📈 Platform Statistics:
   🟢 Active Jobs: 12
   👁️ Public Profiles: 8
   💼 Available Candidates: 6

📊 Application Status Breakdown:
   Pending: 15
   Reviewed: 3
   Shortlisted: 2
   Rejected: 1
   Hired: 0

================================================================================
🎉 ALL TESTS COMPLETED SUCCESSFULLY!
✅ Job Board API is fully functional and ready for production
================================================================================

📊 TEST SUMMARY:
   ✅ Passed: 15
   ❌ Failed: 0
   📈 Success Rate: 100.0%
```

---

## 🛠️ Advanced Testing

### Email Testing

#### Test Email Configuration
```bash
# Open Django shell
python manage.py shell

# Test email sending
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Email',
    'This is a test email from the Job Board API.',
    settings.DEFAULT_FROM_EMAIL,
    ['test@example.com'],
    fail_silently=False,
)
```

### Data Encryption Testing

#### Verify Encryption in Database
```bash
# Open Django shell
python manage.py shell

# Check encryption
from apps.authentication.models import CustomUser
user = CustomUser.objects.first()
print(f"Stored (encrypted): {user.phone_number}")
print(f"Decrypted: {user.phone_number_decrypted}")
```

### API Rate Limiting Testing

```bash
# Test rate limits (run multiple times quickly)
for i in {1..20}; do
  curl -s "http://localhost:8000/api/categories/" > /dev/null
  echo "Request $i completed"
done
```

---

## 🎯 Test Scenarios by User Role

### Job Seeker Workflow

1. **Registration & Profile Setup**
   - Register new account
   - Complete profile information
   - Upload profile image and resume
   - Set availability status

2. **Job Search & Application**
   - Search jobs by criteria
   - View job details
   - Submit applications with cover letters
   - Track application status

3. **Profile Management**
   - Update skills and experience
   - Manage privacy settings
   - View application statistics

### Employer Workflow

1. **Company Setup**
   - Register employer account
   - Complete company profile
   - Set contact information

2. **Job Management**
   - Create job postings
   - Update job requirements
   - Manage application deadlines
   - View job statistics

3. **Application Review**
   - View received applications
   - Update application statuses
   - Contact candidates
   - Track hiring progress

### Admin Workflow

1. **Platform Management**
   - Create and manage categories
   - Monitor user activity
   - Review platform statistics

2. **Content Moderation**
   - Review job postings
   - Manage user accounts
   - Handle support requests

---

## 📈 Performance Benchmarks

### Expected Response Times

- **Authentication endpoints**: < 200ms
- **Job listing (paginated)**: < 300ms
- **Job search with filters**: < 400ms
- **Profile updates**: < 250ms
- **File uploads**: < 2s (depending on file size)

### Scalability Targets

- **Concurrent users**: 100+ simultaneous users
- **API requests**: 1000+ requests per minute
- **Database queries**: Optimized with select_related/prefetch_related
- **File storage**: Supports thousands of profile images and resumes

---

## 🚨 Common Test Failures & Solutions

### Database Connection Issues
```bash
# Check database connectivity
docker exec -it container_name python manage.py check --database default

# Reset database if needed
docker exec -it container_name python manage.py flush
docker exec -it container_name python manage.py migrate
```

### Authentication Failures
```bash
# Verify JWT settings
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Check token expiration
# Access tokens expire in 15 minutes (configurable)
# Refresh tokens expire in 7 days (configurable)
```

### Email Configuration Issues
```bash
# Test email configuration
python manage.py shell -c "
from django.core.mail import send_mail
from django.conf import settings
try:
    send_mail('Test', 'Test message', settings.DEFAULT_FROM_EMAIL, ['test@example.com'])
    print('✅ Email configuration working')
except Exception as e:
    print(f'❌ Email error: {e}')
"
```

---

## 🎉 Testing Completion Checklist

### ✅ Core Functionality
- [ ] User registration and login
- [ ] Password reset with email verification
- [ ] JWT token management
- [ ] Profile creation and updates
- [ ] Job posting and management
- [ ] Application submission and tracking
- [ ] Category management
- [ ] File uploads (images and resumes)

### ✅ Security Features
- [ ] Data encryption for sensitive fields
- [ ] Permission-based access control
- [ ] Input validation and sanitization
- [ ] Token blacklisting on logout
- [ ] Rate limiting (if implemented)
- [ ] CORS configuration

### ✅ API Features
- [ ] Pagination on list endpoints
- [ ] Advanced filtering and search
- [ ] Proper HTTP status codes
- [ ] Comprehensive error handling
- [ ] API documentation accessibility

### ✅ Performance
- [ ] Response times within benchmarks
- [ ] Database query optimization
- [ ] File upload handling
- [ ] Concurrent request handling

---

## 🔗 Additional Resources

- **API Documentation**: [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md)
- **Password Reset Guide**: [`PASSWORD_RESET_README.md`](./PASSWORD_RESET_README.md)
- **Project Presentation**: [`representation.md`](./representation.md)
- **Interactive API Docs**: http://localhost:8000/swagger/
- **Admin Panel**: http://localhost:8000/admin/

---

## 📞 Support

For testing issues or questions:

- **Email**: brahim.chatri.dev@gmail.com
- **GitHub Issues**: Submit detailed bug reports
- **Documentation**: Refer to comprehensive API documentation

---

*This testing guide ensures comprehensive coverage of all Job Board Platform functionality, providing confidence in the system's reliability and security before production deployment.*
