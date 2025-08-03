# Job Board Application Setup Guide

This guide will help you set up the Django Job Board application with encryption and fake data for testing.

## Prerequisites

- Python 3.12 (recommended) or Python 3.8+
- Git
- Internet connection for downloading dependencies

## Quick Setup

### Windows (PowerShell)
```powershell
# Run the setup script
.\setup_app.ps1

# Or with options
.\setup_app.ps1 -SkipData  # Skip fake data loading
.\setup_app.ps1 -Help      # Show help
```

### Linux/Mac (Bash)
```bash
# Make script executable (if needed)
chmod +x setup_app.sh

# Run the setup script
./setup_app.sh

# Or with options
./setup_app.sh --skip-data  # Skip fake data loading
./setup_app.sh --help       # Show help
```

## Manual Setup

If you prefer to set up manually:

### 1. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment (Optional)
Create a `.env` file in the backend directory:
```env
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Load Fake Data (Optional)
```bash
python tests/load_data.py
```

### 6. Start Development Server
```bash
python manage.py runserver
```

## Application URLs

Once the server is running:

- **API Root**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **API Documentation**: http://127.0.0.1:8000/swagger/
- **ReDoc Documentation**: http://127.0.0.1:8000/redoc/

## Test Credentials

The setup script creates test users for you:

### Admin User
- **Username**: `admin`
- **Password**: `admin123`

### Test Users
- **Pattern**: `<firstname><lastname><number>`
- **Password**: `password123`
- **Example**: 
  - Username: `johnsmith1`
  - Password: `password123`

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Users & Profiles
- `GET /api/users/profiles/` - List user profiles
- `GET /api/users/profiles/my_profile/` - Get current user's profile
- `PUT /api/users/profiles/my_profile/` - Update current user's profile

### Jobs
- `GET /api/jobs/` - List all jobs
- `POST /api/jobs/` - Create new job (authenticated)
- `GET /api/jobs/{id}/` - Get job details
- `GET /api/jobs/my_jobs/` - Get current user's posted jobs

### Applications
- `GET /api/applications/` - List applications
- `POST /api/applications/` - Apply for a job
- `GET /api/applications/my_applications/` - Get user's applications

### Categories
- `GET /api/categories/` - List job categories

## Features

### 🔐 Encryption
The application automatically encrypts sensitive user data:
- Personal information (names, phone numbers, addresses)
- User profile bio
- Other sensitive fields as configured

### 📊 Fake Data
The setup includes realistic fake data:
- 25+ test users with profiles
- 10 job categories
- 40+ job postings
- 60+ job applications
- Realistic relationships between entities

### 🎯 API Features
- JWT Authentication with refresh tokens
- Comprehensive filtering and search
- File uploads (profile images, resumes)
- Pagination
- Swagger/OpenAPI documentation
- CORS enabled for frontend development

## Troubleshooting

### Common Issues

1. **Python not found**
   - Install Python 3.12 from python.org
   - Ensure Python is in your PATH

2. **Permission errors (Windows)**
   - Run PowerShell as Administrator
   - Or use: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

3. **Database errors**
   - Delete `db.sqlite3` and run migrations again
   - Check if migrations folder exists in each app

4. **Swagger error**
   - Make sure all serializer fields are included in the `fields` list
   - Check for any missing imports

5. **Encryption errors**
   - Ensure ENCRYPTION_KEY is set in settings
   - Check that cryptography package is installed

### Reset Database
```bash
# Delete database and migrations (be careful!)
rm db.sqlite3
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Recreate migrations and database
python manage.py makemigrations
python manage.py migrate
python tests/load_data.py
```

### Generate New Encryption Key
```bash
python manage.py shell -c "from utils.encryption import generate_encryption_key; print(generate_encryption_key())"
```

## Development Tips

1. **Use the admin panel** for quick data inspection
2. **Check the API docs** at `/swagger/` for endpoint details
3. **Monitor console logs** for debugging information
4. **Use Django shell** for testing: `python manage.py shell`
5. **Run tests** with: `python manage.py test`

## Next Steps

1. Start developing your frontend application
2. Connect to the API endpoints
3. Implement authentication flow
4. Build job listing and application features
5. Customize the data models as needed

## Support

If you encounter issues:
1. Check this README for troubleshooting tips
2. Review the Django and DRF documentation
3. Check the API documentation at `/swagger/`
4. Examine the logs for error details

Happy coding! 🚀
