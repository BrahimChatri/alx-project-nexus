from rest_framework import serializers
from .models import Application
from apps.jobs.models import Job


class JobSummarySerializer(serializers.ModelSerializer):
    """Minimal job info for application serializers"""
    class Meta:
        model = Job
        fields = ['id', 'title', 'company_name', 'location', 'employment_type']


class ApplicationListSerializer(serializers.ModelSerializer):
    job = JobSummarySerializer(read_only=True)
    applicant_username = serializers.CharField(source='applicant.username', read_only=True)
    applicant_email = serializers.CharField(source='applicant.email', read_only=True)
    
    class Meta:
        model = Application
        fields = [
            'id', 'job', 'applicant_username', 'applicant_email',
            'status', 'applied_at', 'updated_at'
        ]


class ApplicationDetailSerializer(serializers.ModelSerializer):
    job = JobSummarySerializer(read_only=True)
    applicant_username = serializers.CharField(source='applicant.username', read_only=True)
    applicant_email = serializers.CharField(source='applicant.email', read_only=True)
    applicant_phone = serializers.SerializerMethodField()
    
    class Meta:
        model = Application
        fields = [
            'id', 'job', 'applicant_username', 'applicant_email', 'applicant_phone',
            'cover_letter', 'resume', 'status', 'applied_at', 'updated_at'
        ]
    
    def get_applicant_phone(self, obj):
        # Decrypt phone number if encrypted
        phone = obj.applicant.phone_number
        if phone:
            from utils.encryption import decrypt_data
            from django.conf import settings
            decrypted = decrypt_data(phone, settings.ENCRYPTION_KEY)
            return decrypted if decrypted else phone
        return None


class ApplicationCreateSerializer(serializers.ModelSerializer):
    job_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Application
        fields = ['job_id', 'cover_letter', 'resume']
    
    def validate_job_id(self, value):
        try:
            job = Job.objects.get(id=value, is_active=True)
            # Check if job is still accepting applications
            if job.application_deadline:
                from django.utils import timezone
                if timezone.now() > job.application_deadline:
                    raise serializers.ValidationError("Application deadline has passed")
        except Job.DoesNotExist:
            raise serializers.ValidationError("Invalid job ID or job is not active")
        return value
    
    def validate(self, attrs):
        job_id = attrs['job_id']
        user = self.context['request'].user
        
        # Check if user already applied to this job
        if Application.objects.filter(job_id=job_id, applicant=user).exists():
            raise serializers.ValidationError("You have already applied to this job")
        
        return attrs
    
    def create(self, validated_data):
        job_id = validated_data.pop('job_id')
        job = Job.objects.get(id=job_id)
        
        application = Application.objects.create(
            job=job,
            applicant=self.context['request'].user,
            **validated_data
        )
        return application


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['status']
    
    def validate_status(self, value):
        if value not in dict(Application.STATUS_CHOICES):
            raise serializers.ValidationError("Invalid status")
        return value


class UserApplicationSerializer(serializers.ModelSerializer):
    """Serializer for applications made by the current user"""
    job = JobSummarySerializer(read_only=True)
    
    class Meta:
        model = Application
        fields = [
            'id', 'job', 'cover_letter', 'resume', 'status',
            'applied_at', 'updated_at'
        ]
