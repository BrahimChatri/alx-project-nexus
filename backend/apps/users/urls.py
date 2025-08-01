from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.profile import UserProfileViewSet

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
