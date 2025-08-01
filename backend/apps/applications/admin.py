from django.contrib import admin
from .models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['job', 'applicant', 'status', 'applied_at', 'updated_at']
    list_filter = ['status', 'applied_at', 'updated_at']
    search_fields = ['job__title', 'job__company_name', 'applicant__username']
    raw_id_fields = ['job', 'applicant']
    date_hierarchy = 'applied_at'
