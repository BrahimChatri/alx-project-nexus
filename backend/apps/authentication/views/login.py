from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.decorators import api_view
from django.http import JsonResponse
from datetime import timedelta
import json
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny

class CustomAccessToken(AccessToken):
    """Custom Access Token with configurable lifetime"""
    
    @classmethod
    def for_user(cls, user, remember_me=False):
        """Create token for user with custom lifetime based on remember_me"""
        token = cls()
        token[cls.token_type] = cls.token_type
        token['user_id'] = user.pk
        
        # Set custom expiration based on remember_me
        if remember_me:
            # Set expiration to 15 days for remember me
            token.set_exp(lifetime=timedelta(days=15))
        else:
            # Set expiration to 1 hour for regular login
            token.set_exp(lifetime=timedelta(hours=1))
        
        return token


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    
    username = data.get("username")
    password = data.get("password")
    remember_me = data.get("remember_me", False)
    
    # Validate required fields
    if not username or not password:
        return JsonResponse({
            "error": "Username and password are required"
        }, status=400)
    
    user = authenticate(username=username, password=password)
    if user is None:
        return JsonResponse({"error": "Invalid credentials"}, status=401)
    
    # Check if user is active
    if not user.is_active:
        return JsonResponse({"error": "User account is disabled"}, status=401)
    
    # Create custom access token with remember me logic
    access_token = CustomAccessToken.for_user(user, remember_me=remember_me)
    
    # Create refresh token if remember_me is True
    refresh_token = None
    if remember_me:
        refresh_token = RefreshToken.for_user(user)
        # Set refresh token to expire in 15 days
        refresh_token.set_exp(lifetime=timedelta(days=15))
    
    # Prepare response data
    response_data = {
        "access": str(access_token),
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": getattr(user, 'full_name', ''),
        },
        "remember_me": remember_me,
        "expires_in": "15 days" if remember_me else "1 hour"
    }
    
    # Add refresh token if remember me is enabled
    if refresh_token:
        response_data["refresh"] = str(refresh_token)
    
    return JsonResponse(response_data, status=200)
