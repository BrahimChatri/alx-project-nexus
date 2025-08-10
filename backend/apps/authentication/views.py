from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework.decorators import api_view, permission_classes, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from datetime import timedelta
import json
import logging
from .models import CustomUser, PasswordResetToken
from .email_utils import send_password_reset_email, send_password_reset_confirmation_email
from django.db import transaction

# Get logger for this module
logger = logging.getLogger('apps.authentication')


# helper function to check password difficulty
def is_password_strong(password):
    return len(password) >= 8 and any(char.isdigit() for char in password) and any(char.isalpha() for char in password)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request) -> JsonResponse:
    data = request.data
    logger.info("User registration attempt initiated")

    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        logger.warning("Registration failed: Username and password required")
        return JsonResponse({"error": "Username and password required"}, status=400)

    if CustomUser.objects.filter(username=username).exists():
        logger.warning(f"Registration failed: Username '{username}' already exists")
        return JsonResponse({"error": "Username already exists"}, status=400)
    
    if not is_password_strong(password):
        logger.warning(f"Registration failed for '{username}': Password does not meet strength requirements")
        return JsonResponse({"error": "Password must be at least 8 characters long and contain both letters and numbers"}, status=400)
        
    # Load data 
    first_name_raw = data.get("first_name")
    last_name_raw = data.get("last_name")
    full_name_raw = data.get("full_name")
    address_raw = data.get("address")
    phone_number_raw = data.get("phone_number")

    if not first_name_raw or not last_name_raw or not full_name_raw:
        logger.warning(f"Registration failed for '{username}': Missing required fields (first_name, last_name, full_name)")
        return JsonResponse({"error": "First name, last name, and full name are required"}, status=400)
    
    try:
        # Create user with raw data - encryption will happen automatically via EncryptedFieldMixin
        user = CustomUser.objects.create_user(
            username=username, 
            password=password, 
            first_name=first_name_raw, 
            last_name=last_name_raw,
            full_name=full_name_raw,
            phone_number=phone_number_raw or '',
            address=address_raw or ''
        )
        logger.info(f"User '{username}' registered successfully with ID: {user.id}")
        return JsonResponse({"message": "User registered successfully"})
    except Exception as e:
        logger.error(f"Failed to create user '{username}': {str(e)}")
        return JsonResponse({"error": "Failed to create user. Please try again."}, status=500)

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
def login_view(request) -> JsonResponse:
    logger.info("Login attempt initiated")
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        logger.error("Login failed: Invalid JSON data received")
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    
    username = data.get("username")
    password = data.get("password")
    remember_me = data.get("remember_me", False)
    
    logger.debug(f"Login attempt for username: '{username}', remember_me: {remember_me}")
    
    # Validate required fields
    if not username or not password:
        logger.warning("Login failed: Missing username or password")
        return JsonResponse({
            "error": "Username and password are required"
        }, status=400)
    
    user = authenticate(username=username, password=password)
    if user is None:
        logger.warning(f"Login failed: Invalid credentials for username '{username}'")
        return JsonResponse({"error": "Invalid credentials"}, status=401)
    
    # Check if user is active
    if not user.is_active:
        logger.warning(f"Login failed: User account '{username}' is disabled")
        return JsonResponse({"error": "User account is disabled"}, status=401)
    
    logger.info(f"User '{username}' authenticated successfully")
    
    # Create custom access token with remember me logic
    access_token = CustomAccessToken.for_user(user, remember_me=remember_me)
    
    # Create refresh token if remember_me is True
    refresh_token = None
    if remember_me:
        refresh_token = RefreshToken.for_user(user)
        # Set refresh token to expire in 15 days
        refresh_token.set_exp(lifetime=timedelta(days=15))
        logger.debug(f"Refresh token created for user '{username}' with 15-day expiry")
    
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
    
    logger.info(f"User '{username}' logged in successfully with {'extended' if remember_me else 'standard'} session")
    return JsonResponse(response_data, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request) -> Response:
    try:
        token = OutstandingToken.objects.get(token=request.auth)
        BlacklistedToken.objects.get_or_create(token=token)
        return Response({"message": "Logged out successfully."})
    except:
        return Response({"error": "Token not found or already blacklisted."}, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_view(request) -> JsonResponse:
    """
    Handle forgot password request - send verification code to user's email
    """
    logger.info("Password reset request initiated")
    
    email = request.data.get('email', '').strip().lower()
    
    if not email:
        logger.warning("Password reset failed: Email not provided")
        return JsonResponse({"error": "Email address is required"}, status=400)
    
    try:
        # Find user by email
        user = CustomUser.objects.get(email=email)
        logger.info(f"Password reset requested for user: {user.username}")
        
        # Create password reset token
        with transaction.atomic():
            reset_token = PasswordResetToken.create_for_user(user)
            
            # Send email with verification code
            email_sent = send_password_reset_email(user, reset_token, request)
            
            if email_sent:
                logger.info(f"Password reset email sent successfully to {email}")
                return JsonResponse({
                    "message": "Password reset code has been sent to your email",
                    "email": email,
                    "token": reset_token.token,  # Include token for frontend to use 
                    "expires_in": "1 hour"
                }, status=200)
            else:
                logger.error(f"Failed to send password reset email to {email}")
                return JsonResponse({
                    "error": "Failed to send email. Please check your email configuration and try again."
                }, status=500)
                
    except CustomUser.DoesNotExist:
        logger.warning(f"Password reset failed: No user found with email {email}")
        # Don't reveal whether email exists or not for security
        return JsonResponse({
            "message": "If an account exists with this email, a password reset code will be sent.",
            "email": email
        }, status=200)
    except Exception as e:
        logger.error(f"Unexpected error during password reset: {str(e)}")
        return JsonResponse({
            "error": "An unexpected error occurred. Please try again later."
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_reset_code_view(request) -> JsonResponse:
    """
    Verify the password reset code entered by user
    """
    logger.info("Password reset code verification initiated")
    
    token = request.data.get('token', '').strip()
    code = request.data.get('code', '').strip()
    
    if not token or not code:
        logger.warning("Code verification failed: Missing token or code")
        return JsonResponse({"error": "Token and verification code are required"}, status=400)
    
    try:
        # Find the reset token
        reset_token = PasswordResetToken.objects.get(token=token, code=code)
        
        # Check if token is valid
        if reset_token.used:
            logger.warning(f"Code verification failed: Token already used for user {reset_token.user.username}")
            return JsonResponse({"error": "This reset code has already been used"}, status=400)
        
        if reset_token.is_expired:
            logger.warning(f"Code verification failed: Token expired for user {reset_token.user.username}")
            return JsonResponse({"error": "This reset code has expired. Please request a new one."}, status=400)
        
        logger.info(f"Password reset code verified successfully for user {reset_token.user.username}")
        return JsonResponse({
            "message": "Verification code is valid",
            "token": token,
            "valid": True
        }, status=200)
        
    except PasswordResetToken.DoesNotExist:
        logger.warning("Code verification failed: Invalid token or code")
        return JsonResponse({"error": "Invalid verification code"}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error during code verification: {str(e)}")
        return JsonResponse({
            "error": "An unexpected error occurred. Please try again."
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_confirm_view(request) -> JsonResponse:
    """
    Reset the user's password after successful code verification
    """
    logger.info("Password reset confirmation initiated")
    
    token = request.data.get('token', '').strip()
    code = request.data.get('code', '').strip()
    new_password = request.data.get('new_password', '')
    confirm_password = request.data.get('confirm_password', '')
    
    # Validate inputs
    if not all([token, code, new_password, confirm_password]):
        logger.warning("Password reset failed: Missing required fields")
        return JsonResponse({
            "error": "All fields are required (token, code, new password, and confirmation)"
        }, status=400)
    
    if new_password != confirm_password:
        logger.warning("Password reset failed: Passwords don't match")
        return JsonResponse({"error": "Passwords do not match"}, status=400)
    
    if not is_password_strong(new_password):
        logger.warning("Password reset failed: Password does not meet strength requirements")
        return JsonResponse({
            "error": "Password must be at least 8 characters long and contain both letters and numbers"
        }, status=400)
    
    try:
        with transaction.atomic():
            # Find and validate the reset token
            reset_token = PasswordResetToken.objects.select_for_update().get(
                token=token,  
                code=code
            )
            
            # Validate token
            is_valid, message = reset_token.validate_and_use()
            if not is_valid:
                logger.warning(f"Password reset failed for user {reset_token.user.username}: {message}")
                return JsonResponse({"error": message}, status=400)
            
            # Reset the user's password
            user = reset_token.user
            user.set_password(new_password)
            user.save()
            
            # Send confirmation email
            send_password_reset_confirmation_email(user)
            
            logger.info(f"Password reset successfully for user {user.username}")
            return JsonResponse({
                "message": "Password has been reset successfully. You can now login with your new password.",
                "success": True
            }, status=200)
            
    except PasswordResetToken.DoesNotExist:
        logger.warning("Password reset failed: Invalid token or code")
        return JsonResponse({"error": "Invalid or expired reset code"}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error during password reset: {str(e)}")
        return JsonResponse({
            "error": "An unexpected error occurred. Please try again."
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_reset_code_view(request) -> JsonResponse:
    """
    Resend the password reset code to user's email
    """
    logger.info("Resend password reset code initiated")
    
    email = request.data.get('email', '').strip().lower()
    
    if not email:
        logger.warning("Resend code failed: Email not provided")
        return JsonResponse({"error": "Email address is required"}, status=400)
    
    try:
        # Find user by email
        user = CustomUser.objects.get(email=email)
        
        # Create new password reset token
        with transaction.atomic():
            reset_token = PasswordResetToken.create_for_user(user)
            
            # Send email with new verification code
            email_sent = send_password_reset_email(user, reset_token, request)
            
            if email_sent:
                logger.info(f"Password reset code resent successfully to {email}")
                return JsonResponse({
                    "message": "A new password reset code has been sent to your email",
                    "email": email,
                    "token": reset_token.token,
                    "expires_in": "1 hour"
                }, status=200)
            else:
                logger.error(f"Failed to resend password reset email to {email}")
                return JsonResponse({
                    "error": "Failed to send email. Please try again later."
                }, status=500)
                
    except CustomUser.DoesNotExist:
        logger.warning(f"Resend code failed: No user found with email {email}")
        # Don't reveal whether email exists or not
        return JsonResponse({
            "message": "If an account exists with this email, a new password reset code will be sent.",
            "email": email
        }, status=200)
    except Exception as e:
        logger.error(f"Unexpected error during code resend: {str(e)}")
        return JsonResponse({
            "error": "An unexpected error occurred. Please try again later."
        }, status=500)
