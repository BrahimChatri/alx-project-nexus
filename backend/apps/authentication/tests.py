from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser

User = get_user_model()


class CustomUserModelTest(TestCase):
    """Test cases for CustomUser model"""

    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123'
        }

    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_superuser(self):
        """Test creating a superuser"""
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertEqual(admin_user.username, 'admin')
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_active)

    def test_user_string_representation(self):
        """Test string representation of user"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'testuser')

    def test_full_name_property(self):
        """Test full_name property"""
        user = User.objects.create_user(**self.user_data)
        expected_full_name = f"{user.first_name} {user.last_name}"
        self.assertEqual(user.full_name, expected_full_name)


class AuthenticationViewsTest(APITestCase):
    """Test cases for authentication views"""

    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123'
        }

    def test_user_registration_success(self):
        """Test successful user registration"""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertIn('access', response.data)
        self.assertIn('user', response.data)

    def test_user_registration_duplicate_username(self):
        """Test registration with duplicate username"""
        User.objects.create_user(**self.user_data)
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_invalid_data(self):
        """Test registration with invalid data"""
        invalid_data = {'username': '', 'password': ''}
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_success(self):
        """Test successful user login"""
        user = User.objects.create_user(**self.user_data)
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('user', response.data)

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        user = User.objects.create_user(**self.user_data)
        login_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_login_nonexistent_user(self):
        """Test login with non-existent user"""
        login_data = {
            'username': 'nonexistent',
            'password': 'password'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_logout_success(self):
        """Test successful user logout"""
        user = User.objects.create_user(**self.user_data)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_logout_unauthenticated(self):
        """Test logout without authentication"""
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_login_with_remember_me_false(self):
        """Test login without remember me (1 hour expiration)"""
        user = User.objects.create_user(**self.user_data)
        login_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'remember_me': False
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['remember_me'], False)
        self.assertEqual(response.data['expires_in'], '1 hour')
        self.assertNotIn('refresh', response.data)  # No refresh token for short-term login

    def test_user_login_with_remember_me_true(self):
        """Test login with remember me (15 days expiration)"""
        user = User.objects.create_user(**self.user_data)
        login_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'remember_me': True
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)  # Should have refresh token
        self.assertIn('user', response.data)
        self.assertEqual(response.data['remember_me'], True)
        self.assertEqual(response.data['expires_in'], '15 days')

    def test_user_login_remember_me_default(self):
        """Test login without remember_me field (should default to False)"""
        user = User.objects.create_user(**self.user_data)
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['remember_me'], False)
        self.assertEqual(response.data['expires_in'], '1 hour')
        self.assertNotIn('refresh', response.data)

    def test_user_login_invalid_json(self):
        """Test login with invalid JSON data"""
        response = self.client.post(
            self.login_url, 
            'invalid json', 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_user_login_missing_fields(self):
        """Test login with missing username or password"""
        # Test missing username
        response = self.client.post(self.login_url, {'password': 'testpass123'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test missing password
        response = self.client.post(self.login_url, {'username': 'testuser'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test both missing
        response = self.client.post(self.login_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_inactive_user(self):
        """Test login with inactive user account"""
        user = User.objects.create_user(**self.user_data)
        user.is_active = False
        user.save()
        
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
