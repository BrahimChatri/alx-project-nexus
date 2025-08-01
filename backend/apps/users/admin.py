from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'job_title', 'company', 'city', 'country', 
        'experience_level', 'is_profile_public', 'is_available_for_hire', 
        'created_at', 'updated_at'
    ]
    list_filter = [
        'experience_level', 'gender', 'is_profile_public', 
        'is_available_for_hire', 'city', 'country', 'created_at'
    ]
    search_fields = [
        'user__username', 'user__email', 'bio', 'job_title', 
        'company', 'skills', 'city', 'country'
    ]
    readonly_fields = ['created_at', 'updated_at', 'age']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Personal Information', {
            'fields': ('bio', 'date_of_birth', 'age', 'gender')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'address', 'city', 'country', 'postal_code')
        }),
        ('Professional Information', {
            'fields': (
                'job_title', 'company', 'experience_level', 
                'expected_salary_min', 'expected_salary_max'
            )
        }),
        ('Skills & Education', {
            'fields': ('skills', 'education', 'certifications')
        }),
        ('Media Files', {
            'fields': ('profile_image', 'resume')
        }),
        ('Social Links', {
            'fields': ('linkedin_url', 'github_url', 'website_url'),
            'classes': ('collapse',)
        }),
        ('Privacy Settings', {
            'fields': ('is_profile_public', 'is_available_for_hire')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
