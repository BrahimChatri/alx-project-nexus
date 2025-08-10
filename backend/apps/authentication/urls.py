from django.urls import path
from .views import (
    login_view, 
    logout_view, 
    register_view, 
    forgot_password_view,
    verify_reset_code_view,
    reset_password_confirm_view,
    resend_reset_code_view
)

urlpatterns = [
    # Authentication endpoints
    path("login/", login_view, name="login_view"),
    path("logout/", logout_view, name="logout_view"),
    path("register/", register_view, name="register_view"),
    
    # Password Reset endpoints
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('verify-reset-code/', verify_reset_code_view, name='verify_reset_code'),
    path('reset-password/', reset_password_confirm_view, name='reset_password_confirm'),
    path('resend-reset-code/', resend_reset_code_view, name='resend_reset_code'),
]
