# Getting Started with Job Board API

## Overview

This guide will help you set up and run the Job Board API using Docker. The API is built with Django REST Framework and provides comprehensive functionality for job posting, job searching, user management, and application tracking.

## Prerequisites

Before starting, make sure you have the following installed on your system:

- **Docker** (v20.0+ recommended)
- **Git** (for cloning the repository)
- **curl** or **Postman** (for testing API endpoints)
- **Supabase account** (for database) or **PostgreSQL** (for local development)

### Installing Docker

#### Windows
1. Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)
2. Run the installer and follow the setup wizard
3. Restart your computer if prompted
4. Verify installation: `docker --version`

#### macOS
1. Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)
2. Drag Docker to Applications folder
3. Launch Docker Desktop
4. Verify installation: `docker --version`

#### Linux (Ubuntu/Debian)
```bash
# Update package index
sudo apt-get update

# Install Docker
sudo apt-get install docker.io docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER

# Verify installation
docker --version
docker-compose --version
```

---

## Quick Start with Docker

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/alx-project-nexus.git
cd alx-project-nexus
```

### 2. Configure Environment

The project uses a `.env` file in the `backend/` directory for configuration. 
Rename the example file `example.env` to `.env`  and update the environment variables as needed:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=*
CORS_ALLOW_ALL_ORIGINS=True
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Database (Supabase or local PostgreSQL)
DB_HOST=your-database-host
DB_PORT=5432
DB_NAME=postgres
DB_USER=your-username
DB_PASSWORD=your-password

# Encryption
ENCRYPTION_KEY=your-32-character-encryption-key

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=15  # minutes
JWT_REFRESH_TOKEN_LIFETIME=7  # days
```

### 3. Build and Run with Docker

The project includes a production-ready Dockerfile that uses Gunicorn:

```bash
# Build the Docker image
docker build -t job-board-api .

# Run the container
docker run -p 8000:8000 --env-file backend/.env job-board-api
```

Alternatively, you can run with environment variables directly:

```bash
docker run -p 8000:8000 \
  -e SECRET_KEY="your-secret-key" \
  -e DEBUG=True \
  -e DB_HOST="your-db-host" \
  -e DB_NAME="your-db-name" \
  -e DB_USER="your-db-user" \
  -e DB_PASSWORD="your-db-password" \
  -e ENCRYPTION_KEY="your-encryption-key" \
  job-board-api
```

### 4. Verify the Installation

Once the containers are running, you can access:

- **API Base URL:** http://localhost:8000/api/
- **Admin Panel:** http://localhost:8000/admin/
- **API Documentation (Swagger):** http://localhost:8000/swagger/
- **API Documentation (ReDoc):** http://localhost:8000/redoc/

### 5. Test the API

Test the API with a simple request:

```bash
# Get all job categories
curl http://localhost:8000/api/categories/

# Register a new user
curl -X POST http://localhost:8000/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123",
    "first_name": "Test",
    "last_name": "User",
    "full_name": "Test User"
  }'

# Login and get token
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123"
  }'
```

---

## Development Setup

### Using Docker for Development

For development, you can run the container with volume mounting for live code reloading:

```bash
# Build development image
docker build -t job-board-api-dev .

# Run with volume mounting for live development
docker run -p 8000:8000 \
  -v $(pwd)/backend:/app \
  -e DEBUG=True \
  -e SECRET_KEY=dev-secret-key \
  -e DB_HOST=your-dev-db-host \
  -e DB_NAME=your-dev-db-name \
  -e DB_USER=your-dev-db-user \
  -e DB_PASSWORD=your-dev-db-password \
  -e ENCRYPTION_KEY=dev-encryption-key-32-chars-long \
  job-board-api-dev
```

### Local Development Without Docker

For local development without Docker:

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env  # Edit with your configuration

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

---

## Environment Configuration

### Environment Variables

The project uses environment variables from the `.env` file in the backend directory. Current configuration supports:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=*
CORS_ALLOW_ALL_ORIGINS=True
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Database (Supabase or PostgreSQL)
DB_HOST=your-database-host
DB_PORT=5432
DB_NAME=postgres
DB_USER=your-username
DB_PASSWORD=your-password

# Encryption
ENCRYPTION_KEY=your-32-character-encryption-key

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=15  # minutes
JWT_REFRESH_TOKEN_LIFETIME=7  # days

# Optional: Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Optional: AWS S3 Configuration
USE_S3=False
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-s3-bucket
AWS_S3_REGION_NAME=us-east-1
```

---

## Database Management

The application automatically handles database migrations and setup through the `entrypoint.sh` script.

### Manual Database Operations

```bash
# Access the running container
docker exec -it <container-name> bash

# Run migrations manually
python manage.py migrate

# Create new migrations
python manage.py makemigrations

# Create superuser
python manage.py createsuperuser

# Populate sample data
python manage.py populate_data
```

### Database Backup (External Database)

Since the application uses an external database (Supabase), backup operations depend on your database provider:

```bash
# For Supabase: Use their dashboard or CLI tools
# For local PostgreSQL: Use pg_dump
pg_dump -h your-host -U your-user -d your-database > backup.sql
```

---

## Common Docker Commands

### Container Management

```bash
# View running containers
docker ps

# View logs from specific container
docker logs <container-id-or-name>
docker logs -f <container-id-or-name>  # Follow logs

# Stop container
docker stop <container-id-or-name>

# Start container
docker start <container-id-or-name>

# Restart container
docker restart <container-id-or-name>

# Remove container
docker rm <container-id-or-name>

# Remove container and associated volumes
docker rm -v <container-id-or-name>
```

### Debugging

```bash
# Execute commands in running container
docker exec -it <container-id-or-name> bash
docker exec -it <container-id-or-name> python manage.py shell

# Run one-off commands
docker run --rm --env-file backend/.env job-board-api python manage.py migrate
docker run --rm --env-file backend/.env job-board-api python manage.py test

# View container resource usage
docker stats
```

---

## Production Deployment

### Production Setup with External Database

Since your setup uses an external database (Supabase), production deployment is straightforward:

```bash
# Build production image
docker build -t job-board-api-prod .

# Run in production mode
docker run -d \
  --name job-board-api \
  -p 8000:8000 \
  --env-file backend/.env \
  --restart unless-stopped \
  job-board-api-prod
```

### Production Environment Variables

For production, update your `.env` file:

```env
# Production Settings
DEBUG=False
SECRET_KEY=your-super-secure-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (Supabase Production)
DB_HOST=your-production-db-host
DB_PORT=5432
DB_NAME=postgres
DB_USER=your-production-db-user
DB_PASSWORD=your-production-db-password

# Encryption (Use different key for production)
ENCRYPTION_KEY=your-production-encryption-key-32-chars

# CORS (Restrict in production)
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues
```bash
# Check if container is running
docker ps

# Check application logs
docker logs <container-name>

# Restart container
docker restart <container-name>
```

#### 2. Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Use different port
docker run -p 8001:8000 --env-file backend/.env job-board-api
```

#### 3. Permission Issues (Linux)
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod -R 755 .
```

#### 4. Docker Build Issues
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t job-board-api .
```

### Logs and Debugging

```bash
# View container logs
docker logs <container-name>

# Follow logs in real-time
docker logs -f <container-name>

# Check Django application status
docker exec -it <container-name> python manage.py check
```

---

## Testing

### Running Tests in Docker

```bash
# Run all tests
docker run --rm --env-file backend/.env job-board-api python manage.py test

# Run specific app tests
docker run --rm --env-file backend/.env job-board-api python manage.py test apps.jobs

# Run with coverage (if coverage is installed)
docker run --rm --env-file backend/.env job-board-api coverage run --source='.' manage.py test
docker run --rm --env-file backend/.env job-board-api coverage report
```

### Load Testing

```bash
# Install Apache Bench (if not installed)
sudo apt-get install apache2-utils  # Linux
brew install apache2-utils  # macOS

# Basic load test
ab -n 1000 -c 10 http://localhost:8000/api/jobs/
```

---

## Monitoring and Maintenance

### Health Checks

The Docker container includes a built-in health check. Monitor with:

```bash
# Check API health
curl http://localhost:8000/api/categories/

# Monitor container health
docker ps  # Look for "healthy" status
```

### Container Maintenance

```bash
# View container resource usage
docker stats <container-name>

# Update container with new image
docker pull job-board-api:latest
docker stop <container-name>
docker rm <container-name>
docker run -d --name job-board-api -p 8000:8000 --env-file backend/.env job-board-api:latest
```

---

## Next Steps

1. **Read the API Documentation:** [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md)
2. **Explore the Admin Panel:** http://localhost:8000/admin/ (admin/admin123)
3. **Test API Endpoints:** Use the interactive documentation at http://localhost:8000/swagger/
4. **Customize Configuration:** Update environment variables and settings as needed
5. **Deploy to Production:** Follow the production deployment guide above

---

## Support

For help and support:

- **Documentation:** Check the [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md) file
- **Issues:** Create an issue on the GitHub repository
- **Contact:** brahim.chatri.dev@gmail.com

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `docker run --rm --env-file backend/.env job-board-api python manage.py test`
5. Submit a pull request

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.
