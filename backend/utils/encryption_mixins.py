"""
Advanced encryption mixins and decorators for Django models
Provides automatic encryption/decryption of sensitive fields
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from typing import List, Dict, Any, Optional
import logging
from .encryption import encrypt_data, decrypt_data, EncryptionError, DecryptionError

logger = logging.getLogger(__name__)


class EncryptedFieldMixin:
    """Mixin to handle encrypted fields in Django models"""
    
    # Override in subclass to specify which fields should be encrypted
    ENCRYPTED_FIELDS: List[str] = []
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_values = {}
        self._decrypted_cache = {}
    
    def save(self, *args, **kwargs):
        """Override save to encrypt sensitive fields before saving"""
        # Encrypt fields before saving
        self._encrypt_fields()
        
        # Call parent save
        super().save(*args, **kwargs)
        
        # Update original values after save
        self._update_original_values()
    
    def refresh_from_db(self, using=None, fields=None):
        """Override refresh to clear decrypted cache"""
        super().refresh_from_db(using=using, fields=fields)
        self._decrypted_cache.clear()
        self._update_original_values()
    
    def _encrypt_fields(self):
        """Encrypt all fields marked for encryption"""
        for field_name in self.ENCRYPTED_FIELDS:
            if hasattr(self, field_name):
                current_value = getattr(self, field_name)
                
                # Only encrypt if value has changed and is not None/empty
                if (current_value and 
                    current_value != self._original_values.get(field_name) and
                    not self._is_already_encrypted(field_name, current_value)):
                    
                    try:
                        encrypted_value = encrypt_data(current_value)
                        setattr(self, field_name, encrypted_value)
                        logger.debug(f"Encrypted field '{field_name}' for {self.__class__.__name__}")
                    except EncryptionError as e:
                        logger.error(f"Failed to encrypt field '{field_name}': {str(e)}")
                        raise ValidationError(f"Failed to encrypt {field_name}: {str(e)}")
    
    def _is_already_encrypted(self, field_name: str, value: str) -> bool:
        """Check if a field value is already encrypted"""
        if not value:
            return False
        
        # Check if value looks like encrypted data (base64 encoded)
        try:
            import base64
            base64.b64decode(value.encode('ascii'))
            # Additional check: encrypted data is typically longer
            return len(value) > 50 and '=' in value
        except:
            return False
    
    def get_decrypted_field(self, field_name: str) -> Optional[str]:
        """Get decrypted value of an encrypted field"""
        if field_name not in self.ENCRYPTED_FIELDS:
            return getattr(self, field_name)
        
        # Check cache first
        if field_name in self._decrypted_cache:
            return self._decrypted_cache[field_name]
        
        encrypted_value = getattr(self, field_name)
        if not encrypted_value:
            return ''
        
        try:
            decrypted_value = decrypt_data(encrypted_value)
            # Cache the decrypted value
            self._decrypted_cache[field_name] = decrypted_value
            return decrypted_value
        except DecryptionError as e:
            logger.error(f"Failed to decrypt field '{field_name}': {str(e)}")
            # Return original value as fallback
            return encrypted_value
    
    def set_field_value(self, field_name: str, value: str):
        """Set field value (will be encrypted on save if field is marked for encryption)"""
        setattr(self, field_name, value)
        # Clear from cache since we're setting a new value
        self._decrypted_cache.pop(field_name, None)
    
    def get_all_decrypted_fields(self) -> Dict[str, str]:
        """Get all decrypted field values as a dictionary"""
        result = {}
        for field_name in self.ENCRYPTED_FIELDS:
            result[field_name] = self.get_decrypted_field(field_name)
        return result
    
    def _update_original_values(self):
        """Update original values for change detection"""
        for field_name in self.ENCRYPTED_FIELDS:
            if hasattr(self, field_name):
                self._original_values[field_name] = getattr(self, field_name)


class EncryptedCharField(models.CharField):
    """Custom CharField that automatically handles encryption/decryption"""
    
    def __init__(self, *args, **kwargs):
        # Encrypted data is typically longer, so adjust max_length
        if 'max_length' in kwargs and kwargs['max_length'] < 500:
            kwargs['max_length'] = 500
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        """Decrypt value when loading from database"""
        if value is None:
            return value
        try:
            return decrypt_data(value)
        except:
            # Return original value if decryption fails
            return value
    
    def to_python(self, value):
        """Convert value to Python representation"""
        if isinstance(value, str) or value is None:
            return value
        return str(value)
    
    def get_prep_value(self, value):
        """Encrypt value before saving to database"""
        if value is None or value == '':
            return value
        
        try:
            # Check if already encrypted
            if self._is_encrypted(value):
                return value
            return encrypt_data(value)
        except:
            # Return original value if encryption fails
            logger.error(f"Failed to encrypt value for {self.name}")
            return value
    
    def _is_encrypted(self, value: str) -> bool:
        """Check if value appears to be encrypted"""
        if not value or len(value) < 50:
            return False
        try:
            import base64
            base64.b64decode(value.encode('ascii'))
            return '=' in value  # Base64 padding
        except:
            return False


def encrypted_property(field_name: str):
    """Decorator to create a property that returns decrypted field value"""
    def decorator(cls):
        def getter(self):
            return self.get_decrypted_field(field_name)
        
        def setter(self, value):
            self.set_field_value(field_name, value)
        
        # Create property with decrypted suffix
        prop_name = f"{field_name}_decrypted"
        setattr(cls, prop_name, property(getter, setter))
        
        return cls
    return decorator


class EncryptionTestMixin:
    """Mixin to test encryption functionality"""
    
    @classmethod
    def test_encryption_roundtrip(cls, test_data: str = "Test Data 123") -> bool:
        """Test encryption and decryption roundtrip"""
        try:
            encrypted = encrypt_data(test_data)
            decrypted = decrypt_data(encrypted)
            return test_data == decrypted
        except Exception as e:
            logger.error(f"Encryption test failed: {str(e)}")
            return False
    
    @classmethod
    def validate_encryption_setup(cls) -> Dict[str, Any]:
        """Validate encryption configuration"""
        from .encryption import is_encryption_enabled, _get_encryption_key
        
        result = {
            'encryption_enabled': is_encryption_enabled(),
            'key_configured': bool(_get_encryption_key()),
            'roundtrip_test': cls.test_encryption_roundtrip(),
            'recommendations': []
        }
        
        if not result['encryption_enabled']:
            result['recommendations'].append(
                "Set a secure ENCRYPTION_KEY in your settings"
            )
        
        if not result['roundtrip_test']:
            result['recommendations'].append(
                "Encryption roundtrip test failed - check your configuration"
            )
        
        return result


# Utility functions for bulk operations
def encrypt_model_fields(model_instance, field_names: List[str]) -> None:
    """Encrypt specific fields of a model instance"""
    for field_name in field_names:
        if hasattr(model_instance, field_name):
            value = getattr(model_instance, field_name)
            if value:
                try:
                    encrypted_value = encrypt_data(value)
                    setattr(model_instance, field_name, encrypted_value)
                except EncryptionError as e:
                    logger.error(f"Failed to encrypt {field_name}: {str(e)}")


def decrypt_model_fields(model_instance, field_names: List[str]) -> Dict[str, str]:
    """Decrypt specific fields of a model instance and return as dict"""
    result = {}
    for field_name in field_names:
        if hasattr(model_instance, field_name):
            encrypted_value = getattr(model_instance, field_name)
            if encrypted_value:
                try:
                    result[field_name] = decrypt_data(encrypted_value)
                except DecryptionError as e:
                    logger.error(f"Failed to decrypt {field_name}: {str(e)}")
                    result[field_name] = encrypted_value  # Fallback to original
            else:
                result[field_name] = ''
    return result


def migrate_to_encrypted_fields(model_class, field_names: List[str], batch_size: int = 100) -> Dict[str, int]:
    """Migrate existing unencrypted data to encrypted format
    
    Args:
        model_class: Django model class
        field_names: List of field names to encrypt
        batch_size: Number of records to process in each batch
        
    Returns:
        Dict with statistics (processed, encrypted, failed)
    """
    stats = {'processed': 0, 'encrypted': 0, 'failed': 0}
    
    # Process in batches to avoid memory issues
    queryset = model_class.objects.all()
    total = queryset.count()
    
    for offset in range(0, total, batch_size):
        batch = queryset[offset:offset + batch_size]
        
        for instance in batch:
            stats['processed'] += 1
            
            try:
                needs_save = False
                for field_name in field_names:
                    if hasattr(instance, field_name):
                        value = getattr(instance, field_name)
                        if value and not _is_already_encrypted_data(value):
                            encrypted_value = encrypt_data(value)
                            setattr(instance, field_name, encrypted_value)
                            needs_save = True
                
                if needs_save:
                    instance.save()
                    stats['encrypted'] += 1
                    
            except Exception as e:
                logger.error(f"Failed to migrate {instance}: {str(e)}")
                stats['failed'] += 1
    
    return stats


def _is_already_encrypted_data(value: str) -> bool:
    """Helper function to check if data is already encrypted"""
    if not value or len(value) < 50:
        return False
    try:
        import base64
        base64.b64decode(value.encode('ascii'))
        return '=' in value
    except:
        return False
