from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PasswordResetToken
from django.utils import timezone


class CustomUserAdmin(UserAdmin):
    """Custom admin configuration for CustomUser"""
    list_display = ['username', 'email', 'is_active', 'is_staff', 'is_admin', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_admin', 'date_joined']
    search_fields = ['username', 'email']
    ordering = ['-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('is_admin', 'full_name', 'phone_number', 'address')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'is_admin', 'full_name', 'phone_number', 'address')
        }),
    )


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """Admin interface for password reset tokens"""
    list_display = ['user', 'code', 'created_at', 'expires_at', 'used', 'is_expired_status']
    list_filter = ['used', 'created_at', 'expires_at']
    search_fields = ['user__username', 'user__email', 'token', 'code']
    readonly_fields = ['token', 'code', 'created_at', 'expires_at']
    ordering = ['-created_at']
    
    def is_expired_status(self, obj):
        """Display whether the token is expired"""
        return obj.is_expired
    is_expired_status.boolean = True
    is_expired_status.short_description = 'Expired'
    
    def has_add_permission(self, request):
        """Prevent manual creation of tokens through admin"""
        return False


# Register the custom user with admin
try:
    admin.site.unregister(CustomUser)  # Unregister first in case it was already registered
except admin.sites.NotRegistered:
    pass  # Model wasn't registered yet, which is fine
admin.site.register(CustomUser, CustomUserAdmin)
