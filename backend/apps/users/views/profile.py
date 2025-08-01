from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from ..models import UserProfile
from ..serializers import (
    UserProfileSerializer, UserProfileUpdateSerializer,
    UserProfilePublicSerializer, UserAccountUpdateSerializer,
    UserStatsSerializer
)

User = get_user_model()


class UserProfileFilter(filters.FilterSet):
    """Custom filter for user profiles"""
    experience_level = filters.ChoiceFilter(choices=UserProfile.EXPERIENCE_LEVEL_CHOICES)
    is_available_for_hire = filters.BooleanFilter()
    city = filters.CharFilter(field_name='city', lookup_expr='icontains')
    country = filters.CharFilter(field_name='country', lookup_expr='icontains')
    skills = filters.CharFilter(field_name='skills', lookup_expr='icontains')
    salary_min = filters.NumberFilter(field_name='expected_salary_min', lookup_expr='gte')
    salary_max = filters.NumberFilter(field_name='expected_salary_max', lookup_expr='lte')
    
    class Meta:
        model = UserProfile
        fields = ['experience_level', 'is_available_for_hire', 'city', 'country', 'skills']


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user profiles
    """
    queryset = UserProfile.objects.filter(is_profile_public=True).select_related('user')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserProfileFilter
    search_fields = ['user__username', 'bio', 'job_title', 'company', 'skills', 'city']
    ordering_fields = ['created_at', 'updated_at', 'expected_salary_min']
    ordering = ['-updated_at']
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserProfileUpdateSerializer
        elif self.action in ['list', 'retrieve'] and not self.is_owner():
            return UserProfilePublicSerializer
        return UserProfileSerializer
    
    def get_permissions(self):
        """
        Set permissions based on action
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.AllowAny]
        
        return [permission() for permission in permission_classes]
    
    def is_owner(self):
        """Check if current user is the profile owner"""
        if hasattr(self, 'get_object'):
            try:
                profile = self.get_object()
                return self.request.user == profile.user
            except:
                return False
        return False
    
    def get_queryset(self):
        """Filter queryset based on action and user"""
        queryset = super().get_queryset()
        
        # For the 'my_profile' action, return only current user's profile
        if self.action == 'my_profile':
            if self.request.user.is_authenticated:
                return UserProfile.objects.filter(user=self.request.user)
            return UserProfile.objects.none()
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create user profile (auto-created, so this updates)"""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileUpdateSerializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            response_serializer = UserProfileSerializer(profile, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Update user profile (only owner can update)"""
        profile = self.get_object()
        
        if profile.user != request.user:
            return Response(
                {'error': 'You can only update your own profile'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Delete user profile (only owner can delete)"""
        profile = self.get_object()
        
        if profile.user != request.user:
            return Response(
                {'error': 'You can only delete your own profile'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def my_profile(self, request):
        """
        Get or update current user's profile
        """
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        if request.method == 'GET':
            serializer = UserProfileSerializer(profile, context={'request': request})
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = UserProfileUpdateSerializer(profile, data=request.data, partial=partial)
            
            if serializer.is_valid():
                serializer.save()
                response_serializer = UserProfileSerializer(profile, context={'request': request})
                return Response(response_serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_stats(self, request):
        """
        Get current user's profile statistics
        """
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserStatsSerializer(profile)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def update_account(self, request):
        """
        Update basic account information (email, password)
        """
        serializer = UserAccountUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Account updated successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def upload_profile_image(self, request, pk=None):
        """
        Upload profile image separately
        """
        profile = self.get_object()
        
        if profile.user != request.user:
            return Response(
                {'error': 'You can only update your own profile'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if 'profile_image' not in request.FILES:
            return Response(
                {'error': 'No image file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = UserProfileUpdateSerializer(
            profile, data={'profile_image': request.FILES['profile_image']}, partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            response_serializer = UserProfileSerializer(profile, context={'request': request})
            return Response({
                'message': 'Profile image updated successfully',
                'profile_image_url': response_serializer.data['profile_image_url']
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def upload_resume(self, request, pk=None):
        """
        Upload resume separately
        """
        profile = self.get_object()
        
        if profile.user != request.user:
            return Response(
                {'error': 'You can only update your own profile'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if 'resume' not in request.FILES:
            return Response(
                {'error': 'No resume file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = UserProfileUpdateSerializer(
            profile, data={'resume': request.FILES['resume']}, partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Resume updated successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def available_candidates(self, request):
        """
        Get profiles of users available for hire (for employers)
        """
        profiles = UserProfile.objects.filter(
            is_profile_public=True, 
            is_available_for_hire=True
        ).select_related('user')
        
        # Apply filters
        filtered_profiles = self.filter_queryset(profiles)
        
        # Paginate
        page = self.paginate_queryset(filtered_profiles)
        if page is not None:
            serializer = UserProfilePublicSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = UserProfilePublicSerializer(filtered_profiles, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def profile_stats(self, request):
        """
        Get general profile statistics
        """
        from django.db.models import Count, Avg
        
        total_profiles = UserProfile.objects.filter(is_profile_public=True).count()
        available_candidates = UserProfile.objects.filter(
            is_profile_public=True, 
            is_available_for_hire=True
        ).count()
        
        # Experience level distribution
        experience_stats = UserProfile.objects.filter(
            is_profile_public=True,
            experience_level__isnull=False
        ).values('experience_level').annotate(count=Count('id'))
        
        # Average expected salary
        avg_salary = UserProfile.objects.filter(
            is_profile_public=True,
            expected_salary_min__isnull=False
        ).aggregate(avg_salary=Avg('expected_salary_min'))
        
        return Response({
            'total_public_profiles': total_profiles,
            'available_candidates': available_candidates,
            'experience_level_distribution': list(experience_stats),
            'average_expected_salary': avg_salary['avg_salary']
        })
