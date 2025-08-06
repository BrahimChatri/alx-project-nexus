from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
import base64
import hashlib
import json
import logging
import os
from typing import Union, Optional, Any, List, Dict
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

# ===== EXCEPTION CLASSES =====
class EncryptionError(Exception):
    """Custom exception for encryption-related errors"""
    pass

class DecryptionError(Exception):
    """Custom exception for decryption-related errors"""
    pass

# ===== CORE ENCRYPTION FUNCTIONS =====
def _generate_key(key: str, salt: Optional[bytes] = None) -> bytes:
    """Generate a Fernet key based on the provided key using PBKDF2"""
    if salt is None:
        # Use a consistent salt for the same key to ensure consistent encryption
        salt = hashlib.sha256(key.encode()).digest()[:16]
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,  # Recommended minimum iterations
    )
    
    key_bytes = kdf.derive(key.encode())
    return base64.urlsafe_b64encode(key_bytes)

def _get_encryption_key() -> str:
    """Get encryption key from settings with fallback"""
    try:
        return getattr(settings, 'ENCRYPTION_KEY', 'default-key-change-this-in-production')
    except:
        # Fallback if Django is not available
        return os.getenv('ENCRYPTION_KEY', 'default-key-change-this-in-production')

def _is_encrypted_data(data: str) -> bool:
    """Check if data appears to be encrypted based on format"""
    if not data or len(data) < 50:
        return False
    
    try:
        # Check if it's valid base64 and has characteristics of encrypted data
        base64.b64decode(data.encode('ascii'))
        # Encrypted data typically contains equals signs and is long
        return '=' in data and len(data) > 50
    except:
        return False

def encrypt_data(data: Union[str, dict, list, int, float, bool], key: Optional[str] = None) -> str:
    """Encrypt given data using Fernet encryption
    
    Args:
        data: Data to encrypt
        key: Encryption key (optional, will use default from settings)
        
    Returns:
        str: Base64 encoded encrypted data
        
    Raises:
        EncryptionError: If encryption fails
    """
    if key is None:
        key = _get_encryption_key()
    
    try:
        # Handle None values
        if data is None:
            return ''
        
        # Convert data to string format
        if isinstance(data, str):
            data_str = data
        elif isinstance(data, (dict, list)):
            data_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        else:
            data_str = str(data)
        
        # Skip encryption for empty strings
        if not data_str.strip():
            return ''
        
        # Check if already encrypted to prevent double encryption
        if _is_encrypted_data(data_str):
            logger.info("Data appears to already be encrypted, skipping encryption")
            return data_str
        
        # Generate encryption key
        fernet_key = _generate_key(key)
        fernet = Fernet(fernet_key)
        
        # Simple encryption without metadata to avoid complexity
        encrypted_bytes = fernet.encrypt(data_str.encode('utf-8'))
        
        # Return base64 encoded string
        return base64.b64encode(encrypted_bytes).decode('ascii')
        
    except Exception as e:
        logger.error(f"Encryption failed: {str(e)}")
        raise EncryptionError(f"Failed to encrypt data: {str(e)}")

def decrypt_data(encrypted_data: str, key: Optional[str] = None) -> str:
    """Decrypt given data using Fernet decryption
    
    Args:
        encrypted_data: Base64 encoded encrypted data
        key: Decryption key (optional, will use default from settings)
        
    Returns:
        str: Decrypted data
        
    Raises:
        DecryptionError: If decryption fails with invalid key/data
    """
    if key is None:
        key = _get_encryption_key()
    
    try:
        # Handle empty or None values
        if not encrypted_data or not encrypted_data.strip():
            return ''
        
        # Check if data might not be encrypted (backward compatibility)
        if not _is_encrypted_data(encrypted_data):
            logger.info("Data appears to be unencrypted, returning as-is")
            return encrypted_data
        
        # Decode from base64
        encrypted_bytes = base64.b64decode(encrypted_data.encode('ascii'))
        
        # Generate decryption key
        fernet_key = _generate_key(key)
        fernet = Fernet(fernet_key)
        
        # Decrypt the data
        decrypted_bytes = fernet.decrypt(encrypted_bytes)
        decrypted_str = decrypted_bytes.decode('utf-8')
        
        return decrypted_str
            
    except (InvalidToken, base64.binascii.Error, ValueError) as e:
        logger.error(f"Decryption failed: {str(e)}")
        raise DecryptionError(f"Failed to decrypt data: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected decryption error: {str(e)}")
        raise DecryptionError(f"Failed to decrypt data: {str(e)}")

# ===== DJANGO MODEL MIXIN =====
class EncryptedFieldMixin:
    """Mixin to handle encrypted fields in Django models"""
    
    # Override in subclass to specify which fields should be encrypted
    ENCRYPTED_FIELDS: List[str] = []
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_values = {}
        self._decrypted_cache = {}
        # Store original values after loading from DB
        self._store_original_values()
    
    def save(self, *args, **kwargs):
        """Override save to encrypt sensitive fields before saving"""
        # Encrypt fields before saving
        self._encrypt_fields()
        
        # Call parent save
        super().save(*args, **kwargs)
        
        # Update original values after save
        self._store_original_values()
    
    def refresh_from_db(self, using=None, fields=None):
        """Override refresh to clear decrypted cache"""
        super().refresh_from_db(using=using, fields=fields)
        self._decrypted_cache.clear()
        self._store_original_values()
    
    def _store_original_values(self):
        """Store original values for change detection"""
        for field_name in self.ENCRYPTED_FIELDS:
            if hasattr(self, field_name):
                self._original_values[field_name] = getattr(self, field_name)
    
    def _encrypt_fields(self):
        """Encrypt all fields marked for encryption"""
        for field_name in self.ENCRYPTED_FIELDS:
            if hasattr(self, field_name):
                current_value = getattr(self, field_name)
                
                # Only encrypt if value exists and has changed
                if (current_value and 
                    current_value != self._original_values.get(field_name)):
                    
                    # Skip if already encrypted
                    if _is_encrypted_data(current_value):
                        continue
                    
                    try:
                        encrypted_value = encrypt_data(current_value)
                        setattr(self, field_name, encrypted_value)
                        logger.debug(f"Encrypted field '{field_name}' for {self.__class__.__name__}")
                    except EncryptionError as e:
                        logger.error(f"Failed to encrypt field '{field_name}': {str(e)}")
                        raise ValidationError(f"Failed to encrypt {field_name}: {str(e)}")
    
    def get_decrypted_field(self, field_name: str) -> str:
        """Get decrypted value of an encrypted field"""
        if field_name not in self.ENCRYPTED_FIELDS:
            return getattr(self, field_name, '')
        
        # Check cache first
        if field_name in self._decrypted_cache:
            return self._decrypted_cache[field_name]
        
        encrypted_value = getattr(self, field_name, '')
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

# ===== DJANGO CUSTOM FIELD =====
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
        except DecryptionError:
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
            return encrypt_data(value)
        except EncryptionError:
            # Return original value if encryption fails
            logger.error(f"Failed to encrypt value for field {self.name}")
            return value

# ===== UTILITY FUNCTIONS =====
def encrypt_dict(data_dict: dict, fields_to_encrypt: list, key: Optional[str] = None) -> dict:
    """Encrypt specific fields in a dictionary"""
    if not isinstance(data_dict, dict):
        raise ValueError("data_dict must be a dictionary")
    
    result = data_dict.copy()
    
    for field in fields_to_encrypt:
        if field in result and result[field] is not None:
            try:
                result[field] = encrypt_data(result[field], key)
            except EncryptionError as e:
                logger.error(f"Failed to encrypt field '{field}': {str(e)}")
    
    return result

def decrypt_dict(data_dict: dict, fields_to_decrypt: list, key: Optional[str] = None) -> dict:
    """Decrypt specific fields in a dictionary"""
    if not isinstance(data_dict, dict):
        raise ValueError("data_dict must be a dictionary")
    
    result = data_dict.copy()
    
    for field in fields_to_decrypt:
        if field in result and result[field] is not None:
            try:
                result[field] = decrypt_data(result[field], key)
            except DecryptionError as e:
                logger.error(f"Failed to decrypt field '{field}': {str(e)}")
    
    return result

def is_encryption_enabled() -> bool:
    """Check if encryption is properly configured"""
    key = _get_encryption_key()
    return key != 'default-key-change-this-in-production'

def generate_encryption_key() -> str:
    """Generate a new secure encryption key"""
    return base64.urlsafe_b64encode(os.urandom(32)).decode('ascii')

def test_encryption_roundtrip(test_data: str = "Test Data 123") -> bool:
    """Test encryption and decryption roundtrip"""
    try:
        encrypted = encrypt_data(test_data)
        decrypted = decrypt_data(encrypted)
        return test_data == decrypted
    except Exception as e:
        logger.error(f"Encryption test failed: {str(e)}")
        return False

def validate_encryption_setup() -> Dict[str, Any]:
    """Validate encryption configuration"""
    result = {
        'encryption_enabled': is_encryption_enabled(),
        'key_configured': bool(_get_encryption_key()),
        'roundtrip_test': test_encryption_roundtrip(),
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

# ===== DATA MIGRATION FUNCTIONS =====
def fix_multiple_encrypted_data(model_class, field_names: List[str], batch_size: int = 100) -> Dict[str, int]:
    """Fix data that has been encrypted multiple times
    
    Args:
        model_class: Django model class
        field_names: List of field names to fix
        batch_size: Number of records to process in each batch
        
    Returns:
        Dict with statistics (processed, fixed, failed)
    """
    stats = {'processed': 0, 'fixed': 0, 'failed': 0, 'skipped': 0}
    
    queryset = model_class.objects.all()
    total = queryset.count()
    
    logger.info(f"Starting to fix multiple encryption for {total} records")
    
    for offset in range(0, total, batch_size):
        batch = queryset[offset:offset + batch_size]
        
        for instance in batch:
            stats['processed'] += 1
            
            try:
                needs_save = False
                for field_name in field_names:
                    if hasattr(instance, field_name):
                        encrypted_value = getattr(instance, field_name)
                        if encrypted_value:
                            # Try to decrypt multiple times until we get readable data
                            decrypted_value = _decrypt_multiple_layers(encrypted_value)
                            if decrypted_value != encrypted_value:
                                # We successfully decrypted, now save the clean data
                                setattr(instance, field_name, decrypted_value)
                                needs_save = True
                
                if needs_save:
                    # Temporarily disable encryption during save to store clean data
                    original_encrypted_fields = getattr(instance, 'ENCRYPTED_FIELDS', [])
                    instance.ENCRYPTED_FIELDS = []
                    instance.save()
                    instance.ENCRYPTED_FIELDS = original_encrypted_fields
                    stats['fixed'] += 1
                else:
                    stats['skipped'] += 1
                    
            except Exception as e:
                logger.error(f"Failed to fix {instance}: {str(e)}")
                stats['failed'] += 1
    
    return stats

def _decrypt_multiple_layers(encrypted_data: str, max_attempts: int = 5) -> str:
    """Attempt to decrypt data that may have been encrypted multiple times"""
    current_data = encrypted_data
    
    for attempt in range(max_attempts):
        try:
            # Try to decrypt
            decrypted = decrypt_data(current_data)
            
            # If the result still looks encrypted, try again
            if _is_encrypted_data(decrypted):
                current_data = decrypted
                continue
            else:
                # We got readable data
                logger.info(f"Successfully decrypted after {attempt + 1} attempts")
                return decrypted
                
        except DecryptionError:
            # Can't decrypt further, return what we have
            break
    
    return current_data
