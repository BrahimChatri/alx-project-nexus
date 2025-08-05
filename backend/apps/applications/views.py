from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters import rest_framework as filters
from django.db.models import Q
import logging

from .models import Application
from .serializers import (
    ApplicationListSerializer, ApplicationDetailSerializer,
    ApplicationCreateSerializer, ApplicationStatusUpdateSerializer,
    UserApplicationSerializer
)

# Get logger for this module
logger = logging.getLogger('apps.applications')


class ApplicationFilter(filters.FilterSet):
    """
    Custom filter for Application model
    """
    status = filters.ChoiceFilter(choices=Application.STATUS_CHOICES)
    job_title = filters.CharFilter(field_name='job__title', lookup_expr='icontains')
    company = filters.CharFilter(field_name='job__company_name', lookup_expr='icontains')
    
    class Meta:
        model = Application
        fields = ['status', 'job_title', 'company']


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing job applications
    """
    queryset = Application.objects.all().select_related('job', 'applicant')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ApplicationFilter
    search_fields = ['job__title', 'job__company_name', 'cover_letter']
    ordering_fields = ['applied_at', 'updated_at', 'status']
    ordering = ['-applied_at']
    
    def get_queryset(self):
        """
        Users can only see applications they made or applications to their jobs
        """
        user = self.request.user

        if not user.is_authenticated:
            return Application.objects.none()

        # For job owners: show applications to their jobs
        if self.action in ['list', 'retrieve'] and 'job_applications' in self.request.path:
            return Application.objects.filter(
                job__posted_by=user
            ).select_related('job', 'applicant')

        # For applicants: show their own applications
        return Application.objects.filter(
            applicant=user
        ).select_related('job', 'applicant')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ApplicationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ApplicationStatusUpdateSerializer
        elif self.action == 'my_applications':
            return UserApplicationSerializer
        elif self.action == 'retrieve':
            return ApplicationDetailSerializer
        return ApplicationListSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new job application
        """
        logger.info(f"User '{request.user.username}' attempting to create job application")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Additional validation: Check if job exists and is active
        job_id = serializer.validated_data['job_id']
        from apps.jobs.models import Job
        
        try:
            job = Job.objects.get(id=job_id, is_active=True)
            logger.debug(f"Job found: '{job.title}' (ID: {job_id})")
        except Job.DoesNotExist:
            logger.warning(f"User '{request.user.username}' tried to apply to non-existent or inactive job (ID: {job_id})")
            return Response(
                {'error': 'Job not found or not active'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user is trying to apply to their own job
        if job.posted_by == request.user:
            logger.warning(f"User '{request.user.username}' tried to apply to their own job '{job.title}' (ID: {job_id})")
            return Response(
                {'error': 'You cannot apply to your own job'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user has already applied to this job
        existing_application = Application.objects.filter(
            job=job, applicant=request.user
        ).first()
        
        if existing_application:
            logger.warning(f"User '{request.user.username}' tried to apply again to job '{job.title}' (ID: {job_id})")
            return Response(
                {'error': 'You have already applied to this job'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        application = serializer.save()
        logger.info(f"Application created successfully: User '{request.user.username}' applied to '{job.title}' (Application ID: {application.id})")
        
        response_serializer = ApplicationDetailSerializer(application, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """
        Only job owners can update application status
        """
        application = self.get_object()
        old_status = application.status
        
        # Check if user is the job owner
        if application.job.posted_by != request.user:
            logger.warning(f"User '{request.user.username}' tried to update application status without permission (Application ID: {application.id})")
            return Response(
                {'error': 'Only job owners can update application status'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        response = super().update(request, *args, **kwargs)
        
        if response.status_code == 200:
            application.refresh_from_db()
            logger.info(f"Application status updated by '{request.user.username}': Application ID {application.id} changed from '{old_status}' to '{application.status}'")
        
        return response
    
    def destroy(self, request, *args, **kwargs):
        """
        Applicants can withdraw their applications
        Job owners cannot delete applications
        """
        application = self.get_object()
        
        # Only applicants can withdraw their applications
        if application.applicant != request.user:
            logger.warning(f"User '{request.user.username}' tried to withdraw someone else's application (Application ID: {application.id})")
            return Response(
                {'error': 'You can only withdraw your own applications'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        logger.info(f"User '{request.user.username}' withdrawing application to '{application.job.title}' (Application ID: {application.id})")
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def my_applications(self, request):
        """
        Get all applications made by the current user
        """
        applications = Application.objects.filter(
            applicant=request.user
        ).select_related('job').order_by('-applied_at')
        
        serializer = UserApplicationSerializer(applications, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def received_applications(self, request):
        """
        Get all applications received for jobs posted by the current user
        """
        applications = Application.objects.filter(
            job__posted_by=request.user
        ).select_related('job', 'applicant').order_by('-applied_at')
        
        serializer = ApplicationListSerializer(applications, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Update application status (for job owners)
        """
        application = self.get_object()
        
        # Check if user is the job owner
        if application.job.posted_by != request.user:
            return Response(
                {'error': 'Only job owners can update application status'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ApplicationStatusUpdateSerializer(
            application, data=request.data, partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            response_serializer = ApplicationDetailSerializer(
                application, context={'request': request}
            )
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get application statistics for the current user
        """
        user_applications = Application.objects.filter(applicant=request.user)
        
        # Count by status
        status_counts = {}
        for status_choice in Application.STATUS_CHOICES:
            status_key = status_choice[0]
            status_counts[status_key] = user_applications.filter(status=status_key).count()
        
        # Recent applications (last 30 days)
        from django.utils import timezone
        from datetime import timedelta
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_applications = user_applications.filter(applied_at__gte=thirty_days_ago).count()
        
        return Response({
            'total_applications': user_applications.count(),
            'status_breakdown': status_counts,
            'recent_applications': recent_applications
        })
