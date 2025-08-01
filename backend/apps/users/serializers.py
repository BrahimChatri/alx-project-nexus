from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile
from utils.encription import decrypt_data
from django.conf import settings

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user information (public view)"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'date_joined']
        read_only_fields = ['id', 'username', 'date_joined']
    
    def get_full_name(self, obj):
        """Decrypt and return full name"""
        if obj.full_name:
            try:
                decrypted = decrypt_data(obj.full_name, settings.ENCRYPTION_KEY)
                return decrypted if decrypted else obj.full_name
            except:
                return obj.full_name
        return None


class UserProfileSerializer(serializers.ModelSerializer):
    """Complete user profile serializer"""
    user = UserBasicSerializer(read_only=True)
    age = serializers.ReadOnlyField()
    skills_list = serializers.ReadOnlyField()
    application_count = serializers.ReadOnlyField()
    jobs_posted_count = serializers.ReadOnlyField()
    profile_image_url = serializers.SerializerMethodField()
    resume_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'bio', 'date_of_birth', 'age', 'gender',
            'phone_number', 'address', 'city', 'country', 'postal_code',
            'job_title', 'company', 'experience_level', 
            'expected_salary_min', 'expected_salary_max',
            'skills', 'skills_list', 'education', 'certifications',
            'profile_image', 'profile_image_url', 'resume', 'resume_url',
            'linkedin_url', 'github_url', 'website_url',
            'is_profile_public', 'is_available_for_hire',
            'application_count', 'jobs_posted_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_profile_image_url(self, obj):
        """Get full URL for profile image"""
        request = self.context.get('request')
        if obj.profile_image and request:
            return request.build_absolute_uri(obj.profile_image.url)
        return None
    
    def get_resume_url(self, obj):
        """Get full URL for resume (only for profile owner)"""
        request = self.context.get('request')
        if obj.resume and request:
            # Only return resume URL to the profile owner
            if request.user == obj.user:
                return request.build_absolute_uri(obj.resume.url)
        return None


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'date_of_birth', 'gender',
            'phone_number', 'address', 'city', 'country', 'postal_code',
            'job_title', 'company', 'experience_level',
            'expected_salary_min', 'expected_salary_max',
            'skills', 'education', 'certifications',
            'profile_image', 'resume',
            'linkedin_url', 'github_url', 'website_url',
            'is_profile_public', 'is_available_for_hire'
        ]
    
    def validate_profile_image(self, value):
        """Validate profile image"""
        if value:
            # Check file size (max 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Profile image size should not exceed 5MB")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError("Only JPEG and PNG images are allowed")
        
        return value
    
    def validate_resume(self, value):
        """Validate resume file"""
        if value:
            # Check file size (max 10MB)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("Resume file size should not exceed 10MB")
            
            # Check file type
            allowed_types = ['application/pdf', 'application/msword', 
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError("Only PDF, DOC, and DOCX files are allowed")
        
        return value
    
    def validate_expected_salary_min(self, value):
        """Validate minimum expected salary"""
        if value and value < 0:
            raise serializers.ValidationError("Salary cannot be negative")
        return value
    
    def validate_expected_salary_max(self, value):
        """Validate maximum expected salary"""
        if value and value < 0:
            raise serializers.ValidationError("Salary cannot be negative")
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        salary_min = attrs.get('expected_salary_min')
        salary_max = attrs.get('expected_salary_max')
        
        if salary_min and salary_max and salary_min > salary_max:
            raise serializers.ValidationError(
                "Minimum expected salary cannot be greater than maximum expected salary"
            )
        
        return attrs


class UserProfilePublicSerializer(serializers.ModelSerializer):
    """Public view of user profile (for employers)"""
    user = UserBasicSerializer(read_only=True)
    age = serializers.ReadOnlyField()
    skills_list = serializers.ReadOnlyField()
    profile_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'user', 'bio', 'age', 'gender', 'city', 'country',
            'job_title', 'company', 'experience_level',
            'expected_salary_min', 'expected_salary_max',
            'skills_list', 'education', 'certifications',
            'profile_image_url', 'linkedin_url', 'github_url', 'website_url',
            'is_available_for_hire'
        ]
    
    def get_profile_image_url(self, obj):
        """Get full URL for profile image"""
        request = self.context.get('request')
        if obj.profile_image and request:
            return request.build_absolute_uri(obj.profile_image.url)
        return None


class UserAccountUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating basic user account information"""
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['email', 'current_password', 'new_password', 'confirm_password']
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        user = self.instance
        if User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("This email is already in use")
        return value
    
    def validate(self, attrs):
        """Validate password change"""
        current_password = attrs.get('current_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        
        if new_password:
            if not current_password:
                raise serializers.ValidationError(
                    "Current password is required to set new password"
                )
            
            if not self.instance.check_password(current_password):
                raise serializers.ValidationError("Current password is incorrect")
            
            if new_password != confirm_password:
                raise serializers.ValidationError("New passwords do not match")
            
            if len(new_password) < 8:
                raise serializers.ValidationError(
                    "New password must be at least 8 characters long"
                )
        
        # Remove password fields from attrs to handle them separately
        attrs.pop('current_password', None)
        attrs.pop('confirm_password', None)
        
        return attrs
    
    def update(self, instance, validated_data):
        """Update user account"""
        new_password = validated_data.pop('new_password', None)
        
        # Update email if provided
        if 'email' in validated_data:
            instance.email = validated_data['email']
        
        # Update password if provided
        if new_password:
            instance.set_password(new_password)
        
        instance.save()
        return instance


class UserStatsSerializer(serializers.Serializer):
    """User statistics serializer"""
    total_applications = serializers.IntegerField()
    pending_applications = serializers.IntegerField()
    successful_applications = serializers.IntegerField()
    total_jobs_posted = serializers.IntegerField()
    active_jobs_posted = serializers.IntegerField()
    profile_completion_percentage = serializers.IntegerField()
    
    def to_representation(self, instance):
        """Calculate user statistics"""
        profile = instance
        user = profile.user
        
        # Application statistics
        applications = user.applications.all()
        total_applications = applications.count()
        pending_applications = applications.filter(status='pending').count()
        successful_applications = applications.filter(status__in=['shortlisted', 'hired']).count()
        
        # Job posting statistics
        jobs = user.posted_jobs.all()
        total_jobs_posted = jobs.count()
        active_jobs_posted = jobs.filter(is_active=True).count()
        
        # Profile completion percentage
        profile_fields = [
            profile.bio, profile.phone_number, profile.job_title,
            profile.skills, profile.education, profile.profile_image
        ]
        completed_fields = sum(1 for field in profile_fields if field)
        profile_completion_percentage = int((completed_fields / len(profile_fields)) * 100)
        
        return {
            'total_applications': total_applications,
            'pending_applications': pending_applications,
            'successful_applications': successful_applications,
            'total_jobs_posted': total_jobs_posted,
            'active_jobs_posted': active_jobs_posted,
            'profile_completion_percentage': profile_completion_percentage
        }
