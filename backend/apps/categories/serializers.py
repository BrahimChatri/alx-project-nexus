from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    job_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'is_active', 'created_at', 'job_count']
        read_only_fields = ['id', 'slug', 'created_at', 'job_count']
    
    def get_job_count(self, obj):
        return obj.jobs.filter(is_active=True).count()


class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'description', 'is_active']
