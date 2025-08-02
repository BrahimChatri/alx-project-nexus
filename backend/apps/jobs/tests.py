from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal
from .models import Job
from apps.categories.models import Category
from apps.users.models import UserProfile

User = get_user_model()


class JobModelTest(TestCase):
    """Test cases for Job model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Technology',
            description='Tech jobs'
        )
        self.job_data = {
            'title': 'Software Engineer',
            'description': 'Looking for a skilled software engineer',
            'company_name': 'Tech Corp',
            'location': 'San Francisco, CA',
            'employment_type': 'full_time',
            'experience_level': 'mid',
            'salary_min': Decimal('80000.00'),
            'salary_max': Decimal('120000.00'),
            'category': self.category,
            'posted_by': self.user
        }

    def test_create_job(self):
        """Test creating a job"""
        job = Job.objects.create(**self.job_data)
        self.assertEqual(job.title, 'Software Engineer')
        self.assertEqual(job.company_name, 'Tech Corp')
        self.assertEqual(job.location, 'San Francisco, CA')
        self.assertEqual(job.employment_type, 'full_time')
        self.assertEqual(job.experience_level, 'mid')
        self.assertEqual(job.salary_min, Decimal('80000.00'))
        self.assertEqual(job.salary_max, Decimal('120000.00'))
        self.assertEqual(job.category, self.category)
        self.assertEqual(job.posted_by, self.user)
        self.assertTrue(job.is_active)

    def test_job_string_representation(self):
        """Test string representation of job"""
        job = Job.objects.create(**self.job_data)
        expected_str = f"{job.title} at {job.company_name}"
        self.assertEqual(str(job), expected_str)

    def test_job_ordering(self):
        """Test job ordering by created_at"""
        job1 = Job.objects.create(**self.job_data)
        job2_data = self.job_data.copy()
        job2_data['title'] = 'Senior Software Engineer'
        job2 = Job.objects.create(**job2_data)
        
        jobs = Job.objects.all()
        self.assertEqual(jobs[0], job2)  # Latest first
        self.assertEqual(jobs[1], job1)

    def test_job_salary_range_property(self):
        """Test salary range property"""
        job = Job.objects.create(**self.job_data)
        expected_range = "$80,000 - $120,000"
        self.assertEqual(job.salary_range, expected_range)

    def test_job_without_salary(self):
        """Test job without salary information"""
        job_data = self.job_data.copy()
        job_data['salary_min'] = None
        job_data['salary_max'] = None
        job = Job.objects.create(**job_data)
        self.assertEqual(job.salary_range, "Salary not specified")


class JobAPITest(APITestCase):
    """Test cases for Job API endpoints"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            bio='Test user bio'
        )
        self.category = Category.objects.create(
            name='Technology',
            description='Tech jobs'
        )
        self.job_data = {
            'title': 'Software Engineer',
            'description': 'Looking for a skilled software engineer',
            'company_name': 'Tech Corp',
            'location': 'San Francisco, CA',
            'employment_type': 'full_time',
            'experience_level': 'mid',
            'salary_min': '80000.00',
            'salary_max': '120000.00',
            'category': self.category.id
        }
        self.job = Job.objects.create(
            title='Existing Job',
            description='Test job',
            company_name='Test Company',
            location='Test Location',
            employment_type='full_time',
            experience_level='junior',
            category=self.category,
            posted_by=self.user
        )

    def get_auth_header(self):
        """Get authorization header for authenticated requests"""
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        return f'Bearer {access_token}'

    def test_job_list_unauthenticated(self):
        """Test job list endpoint without authentication"""
        url = reverse('job-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_job_detail_unauthenticated(self):
        """Test job detail endpoint without authentication"""
        url = reverse('job-detail', kwargs={'pk': self.job.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Existing Job')

    def test_create_job_authenticated(self):
        """Test creating a job with authentication"""
        url = reverse('job-list')
        self.client.credentials(HTTP_AUTHORIZATION=self.get_auth_header())
        response = self.client.post(url, self.job_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Software Engineer')

    def test_create_job_unauthenticated(self):
        """Test creating a job without authentication"""
        url = reverse('job-list')
        response = self.client.post(url, self.job_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_job_owner(self):
        """Test updating job by owner"""
        url = reverse('job-detail', kwargs={'pk': self.job.pk})
        self.client.credentials(HTTP_AUTHORIZATION=self.get_auth_header())
        update_data = {'title': 'Updated Job Title'}
        response = self.client.patch(url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Job Title')

    def test_delete_job_owner(self):
        """Test deleting job by owner"""
        url = reverse('job-detail', kwargs={'pk': self.job.pk})
        self.client.credentials(HTTP_AUTHORIZATION=self.get_auth_header())
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Job.objects.filter(pk=self.job.pk).exists())

    def test_job_filtering_by_employment_type(self):
        """Test filtering jobs by employment type"""
        url = reverse('job-list')
        response = self.client.get(url, {'employment_type': 'full_time'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for job in response.data['results']:
            self.assertEqual(job['employment_type'], 'full_time')

    def test_job_filtering_by_category(self):
        """Test filtering jobs by category"""
        url = reverse('job-list')
        response = self.client.get(url, {'category': self.category.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for job in response.data['results']:
            self.assertEqual(job['category']['id'], self.category.id)

    def test_job_search(self):
        """Test searching jobs"""
        url = reverse('job-list')
        response = self.client.get(url, {'search': 'engineer'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Results should contain jobs with 'engineer' in title or description

    def test_job_ordering(self):
        """Test job ordering"""
        url = reverse('job-list')
        response = self.client.get(url, {'ordering': '-created_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if results are ordered by created_at descending

    def test_invalid_job_data(self):
        """Test creating job with invalid data"""
        url = reverse('job-list')
        self.client.credentials(HTTP_AUTHORIZATION=self.get_auth_header())
        invalid_data = {'title': '', 'company_name': ''}
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
