from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Category
from apps.jobs.models import Job

User = get_user_model()


class CategoryModelTest(TestCase):
    """Test cases for Category model"""

    def setUp(self):
        self.category_data = {
            'name': 'Technology',
            'description': 'Jobs in technology sector'
        }

    def test_create_category(self):
        """Test creating a category"""
        category = Category.objects.create(**self.category_data)
        self.assertEqual(category.name, 'Technology')
        self.assertEqual(category.description, 'Jobs in technology sector')
        self.assertTrue(category.is_active)

    def test_category_string_representation(self):
        """Test string representation of category"""
        category = Category.objects.create(**self.category_data)
        self.assertEqual(str(category), 'Technology')

    def test_category_slug_generation(self):
        """Test automatic slug generation"""
        category = Category.objects.create(
            name='Web Development',
            description='Web development jobs'
        )
        self.assertEqual(category.slug, 'web-development')

    def test_category_job_count_property(self):
        """Test job_count property"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        category = Category.objects.create(**self.category_data)
        
        # Create some jobs in this category
        Job.objects.create(
            title='Software Engineer',
            description='Test job',
            company_name='Test Company',
            location='Test Location',
            category=category,
            posted_by=user
        )
        Job.objects.create(
            title='Python Developer',
            description='Test job 2',
            company_name='Test Company 2',
            location='Test Location 2',
            category=category,
            posted_by=user
        )
        
        self.assertEqual(category.job_count, 2)

    def test_category_unique_name(self):
        """Test category name uniqueness"""
        Category.objects.create(**self.category_data)
        with self.assertRaises(Exception):
            Category.objects.create(**self.category_data)


class CategoryAPITest(APITestCase):
    """Test cases for Category API endpoints"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.category = Category.objects.create(
            name='Technology',
            description='Tech jobs'
        )
        self.category_data = {
            'name': 'Marketing',
            'description': 'Marketing and sales jobs'
        }

    def get_auth_header(self, user=None):
        """Get authorization header for authenticated requests"""
        if user is None:
            user = self.user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return f'Bearer {access_token}'

    def test_category_list_unauthenticated(self):
        """Test category list endpoint without authentication"""
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_category_detail_unauthenticated(self):
        """Test category detail endpoint without authentication"""
        url = reverse('category-detail', kwargs={'pk': self.category.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Technology')

    def test_create_category_admin(self):
        """Test creating a category as admin"""
        url = reverse('category-list')
        self.client.credentials(HTTP_AUTHORIZATION=self.get_auth_header(self.admin_user))
        response = self.client.post(url, self.category_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Marketing')

    def test_create_category_regular_user(self):
        """Test creating a category as regular user (should fail)"""
        url = reverse('category-list')
        self.client.credentials(HTTP_AUTHORIZATION=self.get_auth_header())
        response = self.client.post(url, self.category_data)
        # Depending on permissions, this might be 403 or 401
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_create_category_unauthenticated(self):
        """Test creating a category without authentication"""
        url = reverse('category-list')
        response = self.client.post(url, self.category_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_category_admin(self):
        """Test updating category as admin"""
        url = reverse('category-detail', kwargs={'pk': self.category.pk})
        self.client.credentials(HTTP_AUTHORIZATION=self.get_auth_header(self.admin_user))
        update_data = {'name': 'Updated Technology'}
        response = self.client.patch(url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Technology')

    def test_delete_category_admin(self):
        """Test deleting category as admin"""
        url = reverse('category-detail', kwargs={'pk': self.category.pk})
        self.client.credentials(HTTP_AUTHORIZATION=self.get_auth_header(self.admin_user))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=self.category.pk).exists())

    def test_category_filtering(self):
        """Test filtering categories"""
        Category.objects.create(name='Marketing', description='Marketing jobs')
        url = reverse('category-list')
        response = self.client.get(url, {'search': 'tech'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should find Technology category

    def test_category_ordering(self):
        """Test category ordering"""
        Category.objects.create(name='Marketing', description='Marketing jobs')
        url = reverse('category-list')
        response = self.client.get(url, {'ordering': 'name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Results should be ordered by name

    def test_invalid_category_data(self):
        """Test creating category with invalid data"""
        url = reverse('category-list')
        self.client.credentials(HTTP_AUTHORIZATION=self.get_auth_header(self.admin_user))
        invalid_data = {'name': '', 'description': ''}
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_category_name(self):
        """Test creating category with duplicate name"""
        url = reverse('category-list')
        self.client.credentials(HTTP_AUTHORIZATION=self.get_auth_header(self.admin_user))
        duplicate_data = {'name': 'Technology', 'description': 'Duplicate tech'}
        response = self.client.post(url, duplicate_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
