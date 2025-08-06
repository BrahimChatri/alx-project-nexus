from django.core.management.base import BaseCommand
from faker import Faker
from apps.categories.models import Category
from apps.jobs.models import Job
from apps.authentication.models import CustomUser
from apps.applications.models import Application
from apps.users.models import UserProfile
import random
from datetime import date

class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create Categories
        categories = []
        for _ in range(5):
            category = Category.objects.create(
                name=fake.unique.word().capitalize(),
                description=fake.text(max_nb_chars=200),
            )
            categories.append(category)
        self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} categories'))

        # Create Users
        users = []
        for _ in range(10):
            user = CustomUser.objects.create_user(
                username=fake.unique.user_name(),
                email=fake.email(),
                password='password123',
                is_active=True
            )
            users.append(user)
        self.stdout.write(self.style.SUCCESS(f'Created {len(users)} users'))

        # Create User Profiles
        profiles = []
        skills_list = [
            'Python, Django, REST API',
            'JavaScript, React, Node.js',
            'Java, Spring Boot, MySQL',
            'PHP, Laravel, Vue.js',
            'C#, .NET, SQL Server',
            'Ruby, Rails, PostgreSQL',
            'Go, Docker, Kubernetes',
            'Swift, iOS Development',
            'Android, Kotlin, Firebase',
            'DevOps, AWS, CI/CD'
        ]
        
        for user in users:
            # Generate a random date of birth (25-45 years old)
            birth_year = fake.random_int(min=1979, max=1999)
            birth_date = fake.date_between(
                start_date=date(birth_year, 1, 1),
                end_date=date(birth_year, 12, 31)
            )
            
            profile = UserProfile.objects.create(
                user=user,
                bio=fake.text(max_nb_chars=200),  # Keep shorter for encryption
                date_of_birth=birth_date,
                gender=fake.random_element(elements=('male', 'female', 'other')),
                phone_number=fake.phone_number()[:15],  # Keep shorter for encryption
                address=fake.address()[:100],  # Keep shorter for encryption
                city=fake.city(),
                country=fake.country(),
                postal_code=fake.postcode(),
                job_title=fake.job(),
                company=fake.company(),
                experience_level=fake.random_element(elements=('entry', 'mid', 'senior', 'expert')),
                expected_salary_min=fake.random_int(min=40000, max=80000),
                expected_salary_max=fake.random_int(min=90000, max=150000),
                skills=fake.random_element(elements=skills_list),
                education=f'{fake.random_element(["Bachelor", "Master", "PhD"])} in {fake.random_element(["Computer Science", "Engineering", "Business", "Mathematics"])}',
                certifications=fake.random_element([
                    'AWS Certified Solutions Architect',
                    'Google Cloud Professional',
                    'Microsoft Azure Fundamentals',
                    'Certified Scrum Master',
                    'PMP Certification'
                ]),
                linkedin_url=f'https://linkedin.com/in/{user.username}',
                github_url=f'https://github.com/{user.username}',
                is_profile_public=fake.boolean(chance_of_getting_true=80),
                is_available_for_hire=fake.boolean(chance_of_getting_true=70)
            )
            profiles.append(profile)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(profiles)} user profiles'))

        # Create Jobs
        jobs = []
        for _ in range(20):
            job = Job.objects.create(
                title=fake.job(),
                description=fake.text(max_nb_chars=1000),
                company_name=fake.company(),
                location=fake.city(),
                employment_type=fake.random_element(elements=('full_time', 'part_time', 'contract', 'internship', 'remote')),
                experience_level=fake.random_element(elements=('entry', 'mid', 'senior', 'executive')),
                salary_min=fake.random_int(min=30000, max=50000),
                salary_max=fake.random_int(min=60000, max=100000),
                category=fake.random_element(elements=categories),
                posted_by=fake.random_element(elements=users)
            )
            jobs.append(job)
        self.stdout.write(self.style.SUCCESS(f'Created {len(jobs)} jobs'))

        # Create Applications (avoid duplicates)
        applications = []
        import random
        
        for _ in range(50):
            job = fake.random_element(elements=jobs)
            applicant = fake.random_element(elements=users)
            
            # Skip if application already exists
            if Application.objects.filter(job=job, applicant=applicant).exists():
                continue
                
            # Don't let users apply to their own jobs
            if job.posted_by == applicant:
                continue
                
            application = Application.objects.create(
                job=job,
                applicant=applicant,
                cover_letter=fake.text(max_nb_chars=500),
                status=fake.random_element(elements=Application.STATUS_CHOICES)[0]
            )
            applications.append(application)
            
        self.stdout.write(self.style.SUCCESS(f'Created {len(applications)} applications'))
