from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company_name', 'location', 'employment_type', 'experience_level', 'is_active', 'posted_by', 'created_at']
    list_filter = ['is_active', 'employment_type', 'experience_level', 'category', 'created_at']
    search_fields = ['title', 'company_name', 'location', 'description']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['posted_by', 'category']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'company_name', 'location', 'category')
        }),
        ('Job Details', {
            'fields': ('description', 'requirements', 'benefits', 'employment_type', 'experience_level')
        }),
        ('Salary Information', {
            'fields': ('salary_min', 'salary_max'),
            'classes': ('collapse',)
        }),
        ('Application Details', {
            'fields': ('application_deadline', 'is_active')
        }),
        ('Metadata', {
            'fields': ('posted_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
