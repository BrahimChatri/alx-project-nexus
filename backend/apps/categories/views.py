from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Category
from .serializers import CategorySerializer, CategoryCreateSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing job categories
    """
    queryset = Category.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CategoryCreateSerializer
        return CategorySerializer
    
    def get_permissions(self):
        """
        Instantiate and return the list of permissions.
        Only staff users can create/update/delete categories.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def jobs(self, request, pk=None):
        """
        Get all active jobs in this category
        """
        category = self.get_object()
        from apps.jobs.models import Job
        from apps.jobs.serializers import JobListSerializer
        
        jobs = Job.objects.filter(category=category, is_active=True)
        serializer = JobListSerializer(jobs, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get category statistics
        """
        categories = self.get_queryset()
        stats = []
        
        for category in categories:
            stats.append({
                'id': category.id,
                'name': category.name,
                'job_count': category.jobs.filter(is_active=True).count()
            })
        
        return Response(stats)
