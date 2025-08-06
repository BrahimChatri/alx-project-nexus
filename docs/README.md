# Job Board API Documentation

Welcome to the Job Board API documentation! This comprehensive RESTful API provides functionality for job posting, job searching, user management, and application tracking.

## 📚 Documentation Index

### 🚀 [Getting Started Guide](./GETTING_STARTED.md)
Complete setup instructions using Docker, including:
- Docker installation for Windows, macOS, and Linux
- Quick start with Docker Compose
- Development environment setup
- Production deployment configuration
- Troubleshooting and common issues

### 📖 [API Documentation](./API_DOCUMENTATION.md)
Comprehensive API reference including:
- Authentication and JWT tokens
- User profile management
- Job posting and management
- Application tracking
- Category management
- File uploads and media handling
- Error handling and status codes
- Rate limiting and pagination
- Complete code examples

## 🏗️ Architecture Overview

The Job Board API is built with:

- **Backend**: Django REST Framework
- **Database**: PostgreSQL with encrypted sensitive data
- **Cache**: Redis for session management
- **Authentication**: JWT tokens with refresh capability
- **Documentation**: Swagger/OpenAPI with interactive UI
- **Containerization**: Docker with multi-service setup

## 🔑 Key Features

### 🔐 Security
- **Data Encryption**: Sensitive user data encrypted with AES-256
- **JWT Authentication**: Secure token-based authentication
- **Permission-based Access**: Role-based access control
- **Input Validation**: Comprehensive data validation and sanitization

### 👤 User Management
- **User Registration/Login**: Secure account creation and authentication
- **Profile Management**: Complete user profiles with encrypted PII
- **File Uploads**: Profile images and resume uploads
- **Account Security**: Password management and account settings

### 💼 Job Management
- **Job Posting**: Create and manage job listings
- **Advanced Search**: Filter and search jobs by multiple criteria
- **Categories**: Organized job categories
- **Application Tracking**: Complete application lifecycle management

### 📊 Analytics & Reporting
- **User Statistics**: Profile completion, application tracking
- **Job Statistics**: Application counts, category distribution
- **Performance Metrics**: API usage and response times

## 🛠️ Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/alx-project-nexus.git
cd alx-project-nexus

# Start with Docker Compose
docker build -t job-board-api .

# run docker container
docker run --rm -p 8000:8000 --env-file backend/.env job-board-api

# Access the API
curl http://localhost:8000/api/categories/
```

### Option 2: Development Setup

```bash
# Clone and setup
git clone https://github.com/your-username/alx-project-nexus.git
cd alx-project-nexus/backend

python manage.py migrate  # Apply migrations
python manage.py runserver  # Start the development server
```

## 🌐 API Endpoints Overview

### Authentication
- `POST /auth/register/` - Register new user
- `POST /auth/login/` - User login
- `POST /auth/logout/` - User logout
- `POST /api/token/` - Get JWT token
- `POST /api/token/refresh/` - Refresh JWT token

### User Profiles
- `GET /api/profiles/` - List public profiles
- `GET /account/profiles/my_profile/` - Get current user profile
- `PUT /account/profiles/my_profile/` - Update current user profile
- `GET /account/profiles/my_stats/` - Get user statistics

### Jobs
- `GET /api/jobs/` - List jobs
- `POST /api/jobs/` - Create job
- `GET /api/jobs/{id}/` - Get job details
- `PUT /api/jobs/{id}/` - Update job
- `DELETE /api/jobs/{id}/` - Delete job
- `GET /api/jobs/my_jobs/` - Get user's jobs
- `GET /api/jobs/featured/` - Get featured jobs

### Applications
- `GET /api/applications/` - List applications
- `POST /api/applications/` - Create application
- `GET /api/applications/{id}/` - Get application details
- `DELETE /api/applications/{id}/` - Withdraw application
- `PATCH /api/applications/{id}/update_status/` - Update status

### Categories
- `GET /api/categories/` - List categories
- `POST /api/categories/` - Create category (admin only)
- `GET /api/categories/{id}/` - Get category details
- `GET /api/categories/{id}/jobs/` - Get category jobs

## 📱 Interactive Documentation

Once the API is running, access the interactive documentation:

- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/
- **Admin Panel**: http://localhost:8000/admin/ (admin/admin123)

## 🧪 Testing the API

### Sample API Calls

**Register a User:**
```bash
curl -X POST http://localhost:8000/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePass123",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePass123"
  }'
```

**Search Jobs:**
```bash
curl "http://localhost:8000/api/jobs/?search=python&employment_type=full_time"
```

## 🔧 Configuration

### Environment Variables

Key environment variables for configuration:

```env
# Core Django Settings
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:pass@host:port/db
DB_HOST=db
DB_PORT=5432
DB_NAME=job_board_db
DB_USER=job_board_user
DB_PASSWORD=job_board_password

# Redis
REDIS_URL=redis://redis:6379/0

# Security
ENCRYPTION_KEY=your-32-character-encryption-key

# Email (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 📊 Data Models

### Core Models

- **CustomUser**: Extended user model with encrypted PII
- **UserProfile**: Detailed user profiles with skills, experience
- **Job**: Job postings with full details and requirements
- **Application**: Job applications with status tracking
- **Category**: Job categories for organization

### Data Encryption

Sensitive fields are automatically encrypted:
- Phone numbers
- Addresses
- Bio information
- Personal details

## 🚨 Error Handling

The API uses standard HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (permission denied) 
- `404` - Not Found
- `500` - Internal Server Error

Error responses include detailed messages:

```json
{
  "error": "Validation failed",
  "details": {
    "username": ["This field is required."],
    "password": ["Password must be at least 8 characters."]
  }
}
```

## 📈 Performance

### Rate Limiting
- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour

### Pagination
- Default page size: 20 items
- Maximum page size: 100 items
- Navigation: next/previous URLs provided

### Caching
- Redis caching for session data
- Static file caching via Nginx
- Database query optimization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `docker-compose exec web python manage.py test`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📞 Support

### Getting Help

- **Documentation**: Start with this documentation
- **Interactive API Docs**: http://localhost:8000/swagger/
- **Issues**: Submit issues on GitHub
- **Email**: brahim.chatri.dev@gmail.com

### Common Issues

- **Database Connection**: Check Docker containers are running
- **Port Conflicts**: Ensure ports 8000, 5432, 6379 are available
- **Permission Errors**: Check file permissions for Docker volumes
- **Build Failures**: Clear Docker cache with `docker system prune -a`

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.


---

**Ready to get started?** Check out the [Getting Started Guide](./GETTING_STARTED.md) for detailed setup instructions!
