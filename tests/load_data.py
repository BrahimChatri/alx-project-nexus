#!/usr/bin/env python3
"""
Load fake data for testing the job board application
"""
import os
import sys
import django
from faker import Faker
from datetime import datetime, timedelta
import random

# Add the backend directory to the Python path
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.append(backend_dir)
os.chdir(backend_dir)  # Change to backend directory

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_board.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.categories.models import Category
from apps.jobs.models import Job
from apps.applications.models import Application
from apps.users.models import UserProfile

fake = Faker()
User = get_user_model()

class DataLoader:
    def __init__(self):
        self.users = []
        self.categories = []
        self.jobs = []
        self.profiles = []
        
    def create_categories(self, count=10):
        """Create job categories"""
        print(f"Creating {count} categories...")
        
        categories_data = [
            {"name": "Software Development", "description": "Programming, coding, and software engineering roles"},
            {"name": "Data Science", "description": "Data analysis, machine learning, and AI roles"},
            {"name": "Design", "description": "UI/UX design, graphic design, and creative roles"},
            {"name": "Marketing", "description": "Digital marketing, content creation, and advertising"},
            {"name": "Sales", "description": "Business development and sales positions"},
            {"name": "Customer Support", "description": "Customer service and support roles"},
            {"name": "Project Management", "description": "Project coordination and management positions"},
            {"name": "DevOps", "description": "Infrastructure, deployment, and operations"},
            {"name": "Quality Assurance", "description": "Testing and quality control positions"},
            {"name": "Business Analysis", "description": "Business analysis and consulting roles"},
        ]
        
        for i, cat_data in enumerate(categories_data[:count]):
            category, created = Category.objects.get_or_create(
                name=cat_data["name"],
                defaults={
                    'description': cat_data["description"],
                    'is_active': True,
                }
            )
            if created:
                print(f"  Created category: {category.name}")
            else:
                print(f"  Category already exists: {category.name}")
            self.categories.append(category)
    
    def create_users(self, count=20):
        """Create test users with profiles"""
        print(f"Creating {count} users...")
        
        # Create admin user
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'full_name': 'Admin User',
                'is_admin': True,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            print("  Created admin user (username: admin, password: admin123)")
        self.users.append(admin)
        
        # Create regular users
        for i in range(count - 1):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}{last_name.lower()}{i+1}"
            email = f"{username}@example.com"
            full_name = f"{first_name} {last_name}"
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'full_name': full_name,
                    'is_admin': False,
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                print(f"  Created user: {username}")
            
            self.users.append(user)
    
    def create_user_profiles(self):
        """Create user profiles for all users"""
        print("Creating user profiles...")
        
        skills_list = [
            "Python", "JavaScript", "React", "Django", "Node.js", "PostgreSQL", "MongoDB",
            "AWS", "Docker", "Kubernetes", "Git", "HTML", "CSS", "TypeScript", "Vue.js",
            "Angular", "Express.js", "FastAPI", "Redis", "Elasticsearch", "GraphQL",
            "Machine Learning", "Data Analysis", "SQL", "NoSQL", "Microservices",
            "DevOps", "CI/CD", "Testing", "Agile", "Scrum", "UI/UX Design", "Figma",
            "Adobe Creative Suite", "Project Management", "Leadership", "Communication"
        ]
        
        experience_levels = ['entry', 'mid', 'senior', 'expert']
        genders = ['male', 'female', 'other', 'prefer_not_to_say']
        
        for user in self.users:
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'bio': fake.text(max_nb_chars=500),
                    'date_of_birth': fake.date_of_birth(minimum_age=22, maximum_age=65),
                    'gender': random.choice(genders),
                    'phone_number': fake.phone_number(),
                    'address': fake.address(),
                    'city': fake.city(),
                    'country': fake.country(),
                    'postal_code': fake.postcode(),
                    'job_title': fake.job(),
                    'company': fake.company(),
                    'experience_level': random.choice(experience_levels),
                    'expected_salary_min': random.randint(30000, 80000),
                    'expected_salary_max': random.randint(80000, 150000),
                    'skills': ', '.join(random.sample(skills_list, random.randint(3, 8))),
                    'education': fake.text(max_nb_chars=300),
                    'certifications': fake.text(max_nb_chars=200),
                    'linkedin_url': f"https://linkedin.com/in/{user.username}",
                    'github_url': f"https://github.com/{user.username}",
                    'website_url': fake.url(),
                    'is_profile_public': random.choice([True, True, True, False]),  # 75% public
                    'is_available_for_hire': random.choice([True, True, False]),  # 66% available
                }
            )
            
            if created:
                print(f"  Created profile for: {user.username}")
            
            self.profiles.append(profile)
    
    def create_jobs(self, count=30):
        """Create job postings"""
        print(f"Creating {count} jobs...")
        
        employment_types = ['full_time', 'part_time', 'contract', 'internship', 'freelance']
        experience_levels = ['entry', 'mid', 'senior', 'expert']
        
        job_titles = [
            "Senior Python Developer", "Frontend React Developer", "Full Stack Engineer",
            "Data Scientist", "Machine Learning Engineer", "DevOps Engineer",
            "UI/UX Designer", "Product Manager", "Business Analyst", "QA Engineer",
            "Backend Developer", "Mobile App Developer", "Cloud Architect",
            "Security Engineer", "Database Administrator", "Technical Writer",
            "Scrum Master", "Marketing Manager", "Sales Representative",
            "Customer Success Manager", "HR Specialist", "Financial Analyst",
            "Operations Manager", "Content Creator", "SEO Specialist"
        ]
        
        for i in range(count):
            # Random job poster (employer)
            poster = random.choice(self.users)
            category = random.choice(self.categories)
            
            # Generate job details
            title = random.choice(job_titles)
            company_name = fake.company()
            location = f"{fake.city()}, {fake.country()}"
            employment_type = random.choice(employment_types)
            experience_level = random.choice(experience_levels)
            
            # Salary range based on experience level
            salary_ranges = {
                'entry': (30000, 60000),
                'mid': (60000, 90000),
                'senior': (90000, 130000),
                'expert': (130000, 200000)
            }
            min_sal, max_sal = salary_ranges[experience_level]
            salary_min = random.randint(min_sal, min_sal + 20000)
            salary_max = random.randint(salary_min + 10000, max_sal)
            
            job = Job.objects.create(
                title=title,
                description=fake.text(max_nb_chars=1000),
                requirements=fake.text(max_nb_chars=500),
                company_name=company_name,
                location=location,
                employment_type=employment_type,
                experience_level=experience_level,
                salary_min=salary_min,
                salary_max=salary_max,
                application_deadline=fake.date_between(start_date='+1d', end_date='+90d'),
                category=category,
                posted_by=poster,
                is_active=random.choice([True, True, True, False]),  # 75% active
                created_at=fake.date_time_between(start_date='-30d', end_date='now'),
            )
            
            print(f"  Created job: {title} at {company_name}")
            self.jobs.append(job)
    
    def create_applications(self, count=50):
        """Create job applications"""
        print(f"Creating {count} applications...")
        
        statuses = ['pending', 'reviewed', 'shortlisted', 'rejected', 'hired']
        
        for i in range(count):
            # Random applicant and job
            applicant = random.choice(self.users)
            job = random.choice([j for j in self.jobs if j.is_active])
            
            # Don't let users apply to their own jobs
            if job.posted_by == applicant:
                continue
            
            # Check if application already exists
            if Application.objects.filter(applicant=applicant, job=job).exists():
                continue
            
            application = Application.objects.create(
                applicant=applicant,
                job=job,
                cover_letter=fake.text(max_nb_chars=800),
                status=random.choice(statuses),
                applied_at=fake.date_time_between(start_date=job.created_at, end_date='now'),
            )
            
            print(f"  Created application: {applicant.username} -> {job.title}")
    
    def load_all_data(self):
        """Load all fake data"""
        print("Starting to load fake data...")
        print("=" * 50)
        
        try:
            self.create_categories(10)
            print()
            
            self.create_users(25)
            print()
            
            self.create_user_profiles()
            print()
            
            self.create_jobs(40)
            print()
            
            self.create_applications(60)
            print()
            
            print("=" * 50)
            print("✅ Fake data loaded successfully!")
            print(f"📊 Summary:")
            print(f"   - Users: {User.objects.count()}")
            print(f"   - Profiles: {UserProfile.objects.count()}")
            print(f"   - Categories: {Category.objects.count()}")
            print(f"   - Jobs: {Job.objects.count()}")
            print(f"   - Applications: {Application.objects.count()}")
            print()
            print("🔑 Test credentials:")
            print("   Admin: username=admin, password=admin123")
            print("   Users: username=<firstname><lastname><number>, password=password123")
            print("   Example: username=johnsmith1, password=password123")
            
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            raise

def main():
    """Main function to run the data loader"""
    loader = DataLoader()
    loader.load_all_data()

if __name__ == "__main__":
    main()
