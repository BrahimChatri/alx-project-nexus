from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser
from utils.encryption import encrypt_data, decrypt_data
from django.conf import settings
import re


class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer for CustomUser model with encrypted fields"""
    full_name_decrypted = serializers.SerializerMethodField()
    phone_number_decrypted = serializers.SerializerMethodField()
    address_decrypted = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'full_name_decrypted',
            'phone_number', 'phone_number_decrypted',
            'address', 'address_decrypted',
            'is_admin', 'is_active', 'is_staff', 'date_joined', 'date_created'
        ]
        read_only_fields = ['id', 'date_joined', 'date_created']
    
    def get_full_name_decrypted(self, obj):
        """Decrypt and return full name"""
        if obj.full_name:
            try:
                return decrypt_data(obj.full_name, settings.ENCRYPTION_KEY)
            except:
                return obj.full_name
        return None
    
    def get_phone_number_decrypted(self, obj):
        """Decrypt and return phone number"""
        if obj.phone_number:
            try:
                return decrypt_data(obj.phone_number, settings.ENCRYPTION_KEY)
            except:
                return obj.phone_number
        return None
    
    def get_address_decrypted(self, obj):
        """Decrypt and return address"""
        if obj.address:
            try:
                return decrypt_data(obj.address, settings.ENCRYPTION_KEY)
            except:
                return obj.address
        return None


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration with validation and encryption"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    full_name = serializers.CharField(required=True, max_length=255)
    email = serializers.EmailField(required=True)
    phone_number = serializers.CharField(required=False, max_length=20, allow_blank=True)
    address = serializers.CharField(required=False, max_length=255, allow_blank=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'full_name',
            'phone_number', 'address'
        ]
    
    def validate_username(self, value):
        """Validate username uniqueness and format"""
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long")
        
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("Username can only contain letters, numbers, and underscores")
        
        return value
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def validate_password(self, value):
        """Validate password strength"""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit")
        
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("Password must contain at least one letter")
        
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        
        if not any(char.islower() for char in value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        
        # Use Django's built-in password validation
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        
        return value
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value and not re.match(r'^\+?[\d\s\-\(\)]+$', value):
            raise serializers.ValidationError("Invalid phone number format")
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        
        # Remove password_confirm from attrs as it's not a model field
        attrs.pop('password_confirm')
        return attrs
    
    def create(self, validated_data):
        """Create user with encrypted sensitive data"""
        # Extract password and other data
        password = validated_data.pop('password')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        full_name = validated_data.pop('full_name')
        phone_number = validated_data.pop('phone_number', '')
        address = validated_data.pop('address', '')
        
        # Encrypt sensitive data
        encrypted_first_name = encrypt_data(first_name, settings.ENCRYPTION_KEY)
        encrypted_last_name = encrypt_data(last_name, settings.ENCRYPTION_KEY)
        encrypted_full_name = encrypt_data(full_name, settings.ENCRYPTION_KEY)
        encrypted_phone_number = encrypt_data(phone_number, settings.ENCRYPTION_KEY) if phone_number else ''
        encrypted_address = encrypt_data(address, settings.ENCRYPTION_KEY) if address else ''
        
        # Create user
        user = CustomUser.objects.create_user(
            password=password,
            first_name=encrypted_first_name,
            last_name=encrypted_last_name,
            full_name=encrypted_full_name,
            phone_number=encrypted_phone_number,
            address=encrypted_address,
            **validated_data
        )
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login with remember me functionality"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    remember_me = serializers.BooleanField(default=False)
    
    def validate(self, attrs):
        """Validate login credentials"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if not username or not password:
            raise serializers.ValidationError("Username and password are required")
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")
        
        attrs['user'] = user
        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with user data and remember me support"""
    remember_me = serializers.BooleanField(default=False)
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['is_admin'] = user.is_admin
        
        return token
    
    def validate(self, attrs):
        """Override validation to include user data in response"""
        data = super().validate(attrs)
        
        # Add user data to response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'full_name': getattr(self.user, 'full_name', ''),
            'is_admin': self.user.is_admin,
            'is_active': self.user.is_active,
        }
        
        return data


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)
    password_confirm = serializers.CharField(write_only=True, required=False)
    first_name = serializers.CharField(required=False, max_length=150)
    last_name = serializers.CharField(required=False, max_length=150)
    full_name = serializers.CharField(required=False, max_length=255)
    phone_number = serializers.CharField(required=False, max_length=20, allow_blank=True)
    address = serializers.CharField(required=False, max_length=255, allow_blank=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'address', 'current_password',
            'new_password', 'password_confirm'
        ]
    
    def validate_email(self, value):
        """Validate email uniqueness (excluding current user)"""
        user = self.instance
        if CustomUser.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def validate_new_password(self, value):
        """Validate new password if provided"""
        if value:
            if len(value) < 8:
                raise serializers.ValidationError("Password must be at least 8 characters long")
            
            if not any(char.isdigit() for char in value):
                raise serializers.ValidationError("Password must contain at least one digit")
            
            if not any(char.isalpha() for char in value):
                raise serializers.ValidationError("Password must contain at least one letter")
            
            try:
                validate_password(value)
            except ValidationError as e:
                raise serializers.ValidationError(e.messages)
        
        return value
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value and not re.match(r'^\+?[\d\s\-\(\)]+$', value):
            raise serializers.ValidationError("Invalid phone number format")
        return value
    
    def validate(self, attrs):
        """Cross-field validation for password change"""
        current_password = attrs.get('current_password')
        new_password = attrs.get('new_password')
        password_confirm = attrs.get('password_confirm')
        
        if new_password:
            if not current_password:
                raise serializers.ValidationError("Current password is required to set new password")
            
            if not self.instance.check_password(current_password):
                raise serializers.ValidationError("Current password is incorrect")
            
            if new_password != password_confirm:
                raise serializers.ValidationError("New passwords do not match")
        
        # Remove password fields from attrs as they're handled separately
        attrs.pop('current_password', None)
        attrs.pop('password_confirm', None)
        
        return attrs
    
    def update(self, instance, validated_data):
        """Update user with encrypted sensitive data"""
        new_password = validated_data.pop('new_password', None)
        
        # Encrypt sensitive data if provided
        if 'first_name' in validated_data:
            validated_data['first_name'] = encrypt_data(validated_data['first_name'], settings.ENCRYPTION_KEY)
        
        if 'last_name' in validated_data:
            validated_data['last_name'] = encrypt_data(validated_data['last_name'], settings.ENCRYPTION_KEY)
        
        if 'full_name' in validated_data:
            validated_data['full_name'] = encrypt_data(validated_data['full_name'], settings.ENCRYPTION_KEY)
        
        if 'phone_number' in validated_data:
            validated_data['phone_number'] = encrypt_data(validated_data['phone_number'], settings.ENCRYPTION_KEY)
        
        if 'address' in validated_data:
            validated_data['address'] = encrypt_data(validated_data['address'], settings.ENCRYPTION_KEY)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update password if provided
        if new_password:
            instance.set_password(new_password)
        
        instance.save()
        return instance


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Validate email exists"""
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email address")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    password_confirm = serializers.CharField(required=True)
    
    def validate_new_password(self, value):
        """Validate new password strength"""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit")
        
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("Password must contain at least one letter")
        
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        if attrs['new_password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs


class UserPublicSerializer(serializers.ModelSerializer):
    """Public serializer for user data (no sensitive information)"""
    full_name_decrypted = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'full_name_decrypted', 'date_joined', 'is_admin']
        read_only_fields = ['id', 'username', 'date_joined', 'is_admin']
    
    def get_full_name_decrypted(self, obj):
        """Decrypt and return full name for public display"""
        if obj.full_name:
            try:
                return decrypt_data(obj.full_name, settings.ENCRYPTION_KEY)
            except:
                return "Anonymous User"
        return "Anonymous User"


class TokenRefreshSerializer(serializers.Serializer):
    """Serializer for token refresh with user data"""
    refresh = serializers.CharField()
    
    def validate(self, attrs):
        """Validate refresh token and return new access token"""
        refresh = RefreshToken(attrs['refresh'])
        
        data = {
            'access': str(refresh.access_token),
        }
        
        # Get user data
        try:
            user = CustomUser.objects.get(id=refresh['user_id'])
            data['user'] = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin,
            }
        except CustomUser.DoesNotExist:
            pass
        
        return data
