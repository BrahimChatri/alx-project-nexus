from rest_framework import serializers
from .models import Job
from apps.categories.serializers import CategorySerializer
from apps.authentication.models import CustomUser


class JobListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    posted_by_username = serializers.CharField(source='posted_by.username', read_only=True)
    application_count = serializers.SerializerMethodField()
    days_posted = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company_name', 'location', 'employment_type',
            'experience_level', 'salary_min', 'salary_max', 'category',
            'posted_by_username', 'is_active', 'application_deadline',
            'created_at', 'application_count', 'days_posted'
        ]
    
    def get_application_count(self, obj):
        return obj.applications.count()
    
    def get_days_posted(self, obj):
        from django.utils import timezone
        delta = timezone.now() - obj.created_at
        return delta.days


class JobDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    posted_by_username = serializers.CharField(source='posted_by.username', read_only=True)
    application_count = serializers.SerializerMethodField()
    has_applied = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'description', 'company_name', 'location',
            'employment_type', 'experience_level', 'salary_min', 'salary_max',
            'requirements', 'benefits', 'category', 'posted_by_username',
            'is_active', 'application_deadline', 'created_at', 'updated_at',
            'application_count', 'has_applied'
        ]
    
    def get_application_count(self, obj):
        return obj.applications.count()
    
    def get_has_applied(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.applications.filter(applicant=request.user).exists()
        return False


class JobCreateSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'company_name', 'location',
            'employment_type', 'experience_level', 'salary_min', 'salary_max',
            'requirements', 'benefits', 'category_id', 'application_deadline'
        ]
    
    def validate_category_id(self, value):
        from apps.categories.models import Category
        try:
            Category.objects.get(id=value, is_active=True)
        except Category.DoesNotExist:
            raise serializers.ValidationError("Invalid category ID")
        return value
    
    def create(self, validated_data):
        category_id = validated_data.pop('category_id')
        from apps.categories.models import Category
        category = Category.objects.get(id=category_id)
        
        job = Job.objects.create(
            category=category,
            posted_by=self.context['request'].user,
            **validated_data
        )
        return job


class JobUpdateSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'company_name', 'location',
            'employment_type', 'experience_level', 'salary_min', 'salary_max',
            'requirements', 'benefits', 'category_id', 'application_deadline', 'is_active'
        ]
    
    def validate_category_id(self, value):
        from apps.categories.models import Category
        try:
            Category.objects.get(id=value, is_active=True)
        except Category.DoesNotExist:
            raise serializers.ValidationError("Invalid category ID")
        return value
    
    def update(self, instance, validated_data):
        category_id = validated_data.pop('category_id', None)
        if category_id:
            from apps.categories.models import Category
            category = Category.objects.get(id=category_id)
            instance.category = category
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
