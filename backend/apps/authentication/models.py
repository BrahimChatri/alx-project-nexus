from django.db import models
from django.contrib.auth.models import AbstractUser
from utils.encryption import EncryptedFieldMixin
from django.conf import settings
from django.utils import timezone
import secrets
import string
from datetime import timedelta

class CustomUser(EncryptedFieldMixin, AbstractUser):
    """Custom user model with encrypted sensitive fields"""
    
    # Fields to encrypt
    ENCRYPTED_FIELDS = ['first_name', 'last_name', 'full_name', 'phone_number', 'address']

    # Override inherited fields to allow for encrypted values
    first_name = models.CharField(max_length=500, blank=True)
    last_name = models.CharField(max_length=500, blank=True)

    full_name = models.CharField(max_length=500, null=True, blank=True)
    phone_number = models.CharField(max_length=500, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
    
    def __str__(self):
        return self.username
    
    @property
    def full_name_decrypted(self):
        """Get decrypted full name"""
        return self.get_decrypted_field('full_name')
    
    @property
    def first_name_decrypted(self):
        """Get decrypted first name"""
        return self.get_decrypted_field('first_name')
    
    @property
    def last_name_decrypted(self):
        """Get decrypted last name"""
        return self.get_decrypted_field('last_name')
    
    @property
    def phone_number_decrypted(self):
        """Get decrypted phone number"""
        return self.get_decrypted_field('phone_number')
    
    @property
    def address_decrypted(self):
        """Get decrypted address"""
        return self.get_decrypted_field('address')
    
    def get_display_name(self):
        """Get user's display name (full name if available, otherwise username)"""
        full_name = self.full_name_decrypted
        if full_name and full_name.strip():
            return full_name
        return self.username
    
    def get_short_name(self):
        """Get user's short name (first name if available, otherwise username)"""
        first_name = self.first_name_decrypted
        if first_name and first_name.strip():
            return first_name
        return self.username
    
    def save(self, *args, **kwargs):
        """Override save to handle encryption"""
        # Ensure email is lowercase
        if self.email:
            self.email = self.email.lower().strip()
        
        # Call parent save (which will handle encryption)
        super().save(*args, **kwargs)


class PasswordResetToken(models.Model):
    """Model to store password reset tokens"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=6)  # 6-digit verification code
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['code', 'user']),
        ]
    
    def __str__(self):
        return f"Password reset token for {self.user.username}"
    
    @property
    def is_expired(self):
        """Check if the token has expired"""
        return timezone.now() > self.expires_at
    
    @classmethod
    def generate_token(cls):
        """Generate a secure random token"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(64))
    
    @classmethod
    def generate_code(cls):
        """Generate a 6-digit verification code"""
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    
    @classmethod
    def create_for_user(cls, user):
        """Create a new password reset token for a user"""
        # Invalidate all previous tokens for this user
        cls.objects.filter(user=user, used=False).update(used=True)
        
        # Create new token
        token = cls.objects.create(
            user=user,
            token=cls.generate_token(),
            code=cls.generate_code(),
            expires_at=timezone.now() + timedelta(hours=1)  # Token expires in 1 hour
        )
        return token
    
    def validate_and_use(self):
        """Validate the token and mark it as used"""
        if self.used:
            return False, "This reset token has already been used."
        
        if self.is_expired:
            return False, "This reset token has expired."
        
        self.used = True
        self.save()
        return True, "Token validated successfully."
