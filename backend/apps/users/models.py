from django.db import models
from django.conf import settings
from django.utils import timezone
from PIL import Image
import os


def user_profile_image_path(instance, filename):
    """Generate file path for user profile images"""
    ext = filename.split('.')[-1]
    filename = f"profile_{instance.user.id}.{ext}"
    return os.path.join('profiles', filename)


def user_resume_path(instance, filename):
    """Generate file path for user resumes"""
    ext = filename.split('.')[-1]
    filename = f"resume_{instance.user.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    return os.path.join('resumes', filename)


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]
    
    EXPERIENCE_LEVEL_CHOICES = [
        ('entry', 'Entry Level (0-2 years)'),
        ('mid', 'Mid Level (3-5 years)'),
        ('senior', 'Senior Level (6-10 years)'),
        ('expert', 'Expert Level (10+ years)'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    
    # Personal Information
    bio = models.TextField(max_length=1000, blank=True, help_text="Brief description about yourself")
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    
    # Contact Information (extends the user model)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Professional Information
    job_title = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=200, blank=True)
    experience_level = models.CharField(
        max_length=20, 
        choices=EXPERIENCE_LEVEL_CHOICES, 
        blank=True
    )
    expected_salary_min = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Minimum expected salary"
    )
    expected_salary_max = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Maximum expected salary"
    )
    
    # Skills and Education
    skills = models.TextField(
        blank=True, 
        help_text="Comma-separated list of skills"
    )
    education = models.TextField(blank=True, help_text="Educational background")
    certifications = models.TextField(blank=True, help_text="Professional certifications")
    
    # Media Files
    profile_image = models.ImageField(
        upload_to=user_profile_image_path, 
        blank=True, 
        null=True,
        help_text="Profile picture"
    )
    resume = models.FileField(
        upload_to=user_resume_path, 
        blank=True, 
        null=True,
        help_text="Upload your resume (PDF, DOC, DOCX)"
    )
    
    # Social Links
    linkedin_url = models.URLField(blank=True, help_text="LinkedIn profile URL")
    github_url = models.URLField(blank=True, help_text="GitHub profile URL")
    website_url = models.URLField(blank=True, help_text="Personal website URL")
    
    # Privacy Settings
    is_profile_public = models.BooleanField(
        default=True, 
        help_text="Make profile visible to employers"
    )
    is_available_for_hire = models.BooleanField(
        default=True, 
        help_text="Available for job opportunities"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize profile image if it's too large
        if self.profile_image:
            try:
                img = Image.open(self.profile_image.path)
                if img.height > 500 or img.width > 500:
                    img.thumbnail((500, 500), Image.Resampling.LANCZOS)
                    img.save(self.profile_image.path, optimize=True, quality=85)
            except Exception as e:
                # Log the error but don't fail the save
                print(f"Error resizing image: {e}")
    
    @property
    def age(self):
        """Calculate age from date of birth"""
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    @property
    def skills_list(self):
        """Return skills as a list"""
        if self.skills:
            return [skill.strip() for skill in self.skills.split(',') if skill.strip()]
        return []
    
    @property
    def application_count(self):
        """Get total number of applications submitted"""
        return self.user.applications.count()
    
    @property
    def jobs_posted_count(self):
        """Get total number of jobs posted by this user"""
        return self.user.posted_jobs.count()
