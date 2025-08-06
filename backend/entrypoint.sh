#!/bin/bash
set -e

echo "Checking for pending model changes..."
if python manage.py makemigrations --check --dry-run | grep -q "Migrations for"; then
    echo "Unapplied model changes detected. Generating migrations..."
    python manage.py makemigrations
else
    echo "No new migrations needed."
fi

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser if not exists..."
python manage.py shell << END
from django.contrib.auth import get_user_model
import os

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if username and password:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email or '', password=password)
        print("Superuser created.")
    else:
        print("Superuser already exists.")
else:
    print("Superuser env vars not set; skipping creation.")
END

echo "starting load script to load data in db "
python load_data.py

echo "Starting Gunicorn..."
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --worker-class sync \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 30 \
    --keep-alive 2 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    job_board.wsgi:application
