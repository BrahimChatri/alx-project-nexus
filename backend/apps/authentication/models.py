from django.db import models
from django.contrib.auth.models import AbstractUser
from utils.encryption_mixins import EncryptedFieldMixin, EncryptionTestMixin
from utils.encryption import decrypt_data
from django.conf import settings

class CustomUser(EncryptedFieldMixin, EncryptionTestMixin, AbstractUser):
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
