from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters import rest_framework as filters
from django.db.models import Q

from .models import Job
from .serializers import (
    JobListSerializer, JobDetailSerializer, 
    JobCreateSerializer, JobUpdateSerializer
)


class JobFilter(filters.FilterSet):
    """
    Custom filter for Job model
    """
    salary_min = filters.NumberFilter(field_name='salary_min', lookup_expr='gte')
    salary_max = filters.NumberFilter(field_name='salary_max', lookup_expr='lte')
    location = filters.CharFilter(field_name='location', lookup_expr='icontains')
    company = filters.CharFilter(field_name='company_name', lookup_expr='icontains')
    employment_type = filters.ChoiceFilter(choices=Job.EMPLOYMENT_TYPE_CHOICES)
    experience_level = filters.ChoiceFilter(choices=Job.EXPERIENCE_LEVEL_CHOICES)
    category = filters.NumberFilter(field_name='category__id')
    
    class Meta:
        model = Job
        fields = ['salary_min', 'salary_max', 'location', 'company', 
                 'employment_type', 'experience_level', 'category']


class JobViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing job postings
    """
    queryset = Job.objects.filter(is_active=True).select_related('category', 'posted_by')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = JobFilter
    search_fields = ['title', 'description', 'company_name', 'location', 'requirements']
    ordering_fields = ['created_at', 'application_deadline', 'salary_min', 'salary_max']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return JobListSerializer
        elif self.action == 'create':
            return JobCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return JobUpdateSerializer
        return JobDetailSerializer
    
    def get_permissions(self):
        """
        Only authenticated users can create jobs.
        Only job owners can update/delete their jobs.
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.AllowAny]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # If user wants to see their own jobs (including inactive ones)
        if self.action == 'my_jobs':
            if self.request.user.is_authenticated:
                queryset = Job.objects.filter(posted_by=self.request.user).select_related('category')
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """
        Only allow job owner to update their job
        """
        job = self.get_object()
        if job.posted_by != request.user:
            return Response(
                {'error': 'You can only update your own job postings'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Only allow job owner to delete their job
        """
        job = self.get_object()
        if job.posted_by != request.user:
            return Response(
                {'error': 'You can only delete your own job postings'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_jobs(self, request):
        """
        Get jobs posted by the current user
        """
        jobs = Job.objects.filter(posted_by=request.user).select_related('category')
        serializer = JobListSerializer(jobs, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def applications(self, request, pk=None):
        """
        Get all applications for this job (only for job owner)
        """
        job = self.get_object()
        if job.posted_by != request.user:
            return Response(
                {'error': 'You can only view applications for your own jobs'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        from apps.applications.models import Application
        from apps.applications.serializers import ApplicationListSerializer
        
        applications = Application.objects.filter(job=job).select_related('applicant')
        serializer = ApplicationListSerializer(applications, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Get featured jobs (most recent or most applied to)
        """
        from django.db.models import Count
        
        jobs = self.get_queryset().annotate(
            application_count=Count('applications')
        ).order_by('-application_count', '-created_at')[:10]
        
        serializer = JobListSerializer(jobs, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get job statistics
        """
        from django.db.models import Count, Avg
        from apps.applications.models import Application
        
        total_jobs = self.get_queryset().count()
        total_applications = Application.objects.count()
        
        # Employment type distribution
        employment_stats = Job.objects.filter(is_active=True).values('employment_type').annotate(
            count=Count('id')
        )
        
        # Average salary by experience level
        salary_stats = Job.objects.filter(
            is_active=True, 
            salary_min__isnull=False
        ).values('experience_level').annotate(
            avg_salary=Avg('salary_min')
        )
        
        return Response({
            'total_jobs': total_jobs,
            'total_applications': total_applications,
            'employment_type_distribution': list(employment_stats),
            'average_salary_by_level': list(salary_stats)
        })
