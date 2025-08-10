"""Email utility functions for authentication"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger('apps.authentication')


def send_password_reset_email(user, reset_token, request=None):
    """
    Send password reset email with verification code
    
    Args:
        user: User object
        reset_token: PasswordResetToken object
        request: HTTP request object (optional, for building absolute URLs)
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Build reset URL if request is provided
        reset_url = None
        if request:
            protocol = 'https' if request.is_secure() else 'http'
            domain = request.get_host()
            reset_url = f"{protocol}://{domain}/reset-password/{reset_token.token}"
        
        # Email context
        context = {
            'user': user,
            'username': user.username,
            'email': user.email,
            'verification_code': reset_token.code,
            'reset_url': reset_url,
            'expires_in': '1 hour',
            'support_email': settings.DEFAULT_FROM_EMAIL,
        }
        
        # Email subject
        subject = 'Password Reset Request - Verification Code'
        
        # Email body (HTML)
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                        Password Reset Request
                    </h2>
                    
                    <p>Hello <strong>{user.username}</strong>,</p>
                    
                    <p>We received a request to reset your password for your account associated with <strong>{user.email}</strong>.</p>
                    
                    <div style="background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 20px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #495057;">Your Verification Code:</h3>
                        <p style="font-size: 32px; font-weight: bold; color: #007bff; letter-spacing: 5px; text-align: center; margin: 15px 0;">
                            {reset_token.code}
                        </p>
                        <p style="text-align: center; color: #6c757d; font-size: 14px;">
                            This code will expire in <strong>1 hour</strong>
                        </p>
                    </div>
                    
                    {f'''
                    <p>Alternatively, you can reset your password by clicking the link below:</p>
                    <p style="text-align: center; margin: 20px 0;">
                        <a href="{reset_url}" style="display: inline-block; padding: 12px 30px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                            Reset Password
                        </a>
                    </p>
                    ''' if reset_url else ''}
                    
                    <div style="background-color: #fff3cd; border: 1px solid #ffeeba; border-radius: 5px; padding: 15px; margin: 20px 0;">
                        <p style="margin: 0; color: #856404;">
                            <strong>Security Notice:</strong> If you didn't request this password reset, please ignore this email. 
                            Your password won't be changed unless you enter the verification code or click the reset link above.
                        </p>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #dee2e6; margin: 30px 0;">
                    
                    <p style="color: #6c757d; font-size: 14px;">
                        Best regards,<br>
                        The Support Team<br>
                        <a href="mailto:{settings.DEFAULT_FROM_EMAIL}" style="color: #007bff;">{settings.DEFAULT_FROM_EMAIL}</a>
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Plain text version
        plain_message = f"""
Password Reset Request

Hello {user.username},

We received a request to reset your password for your account associated with {user.email}.

Your Verification Code: {reset_token.code}

This code will expire in 1 hour.

{f'Alternatively, you can reset your password by visiting: {reset_url}' if reset_url else ''}

Security Notice: If you didn't request this password reset, please ignore this email. 
Your password won't be changed unless you enter the verification code or use the reset link.

Best regards,
The Support Team
{settings.DEFAULT_FROM_EMAIL}
        """
        
        # Send email
        sent = send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        if sent:
            logger.info(f"Password reset email sent successfully to {user.email}")
            return True
        else:
            logger.error(f"Failed to send password reset email to {user.email}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending password reset email to {user.email}: {str(e)}")
        return False


def send_password_reset_confirmation_email(user):
    """
    Send confirmation email after successful password reset
    
    Args:
        user: User object
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        subject = 'Password Reset Successful'
        
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #28a745; border-bottom: 2px solid #28a745; padding-bottom: 10px;">
                        Password Reset Successful
                    </h2>
                    
                    <p>Hello <strong>{user.username}</strong>,</p>
                    
                    <p>Your password has been successfully reset for the account associated with <strong>{user.email}</strong>.</p>
                    
                    <div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; margin: 20px 0;">
                        <p style="margin: 0; color: #155724;">
                            You can now log in with your new password.
                        </p>
                    </div>
                    
                    <div style="background-color: #fff3cd; border: 1px solid #ffeeba; border-radius: 5px; padding: 15px; margin: 20px 0;">
                        <p style="margin: 0; color: #856404;">
                            <strong>Security Notice:</strong> If you didn't make this change, please contact our support team immediately 
                            at <a href="mailto:{settings.DEFAULT_FROM_EMAIL}" style="color: #007bff;">{settings.DEFAULT_FROM_EMAIL}</a>
                        </p>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #dee2e6; margin: 30px 0;">
                    
                    <p style="color: #6c757d; font-size: 14px;">
                        Best regards,<br>
                        The Support Team<br>
                        <a href="mailto:{settings.DEFAULT_FROM_EMAIL}" style="color: #007bff;">{settings.DEFAULT_FROM_EMAIL}</a>
                    </p>
                </div>
            </body>
        </html>
        """
        
        plain_message = f"""
Password Reset Successful

Hello {user.username},

Your password has been successfully reset for the account associated with {user.email}.

You can now log in with your new password.

Security Notice: If you didn't make this change, please contact our support team immediately at {settings.DEFAULT_FROM_EMAIL}

Best regards,
The Support Team
{settings.DEFAULT_FROM_EMAIL}
        """
        
        sent = send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        if sent:
            logger.info(f"Password reset confirmation email sent to {user.email}")
            return True
        else:
            logger.error(f"Failed to send password reset confirmation email to {user.email}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending password reset confirmation email to {user.email}: {str(e)}")
        return False
