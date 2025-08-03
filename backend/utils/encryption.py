from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import hashlib
import json
import logging
import os
from typing import Union, Optional, Any
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

class EncryptionError(Exception):
    """Custom exception for encryption-related errors"""
    pass

class DecryptionError(Exception):
    """Custom exception for decryption-related errors"""
    pass

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
        from django.conf import settings
        return getattr(settings, 'ENCRYPTION_KEY', 'default-key-change-this-in-production')
    except ImportError:
        # Fallback if Django is not available
        return os.getenv('ENCRYPTION_KEY', 'default-key-change-this-in-production')

def encrypt_data(data: Union[str, dict, list, int, float, bool], key: Optional[str] = None) -> str:
    """Encrypt given data using Fernet encryption with improved security
    
    Args:
        data: Data to encrypt (str, dict, list, int, float, bool)
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
        elif isinstance(data, (int, float, bool)):
            data_str = str(data)
        else:
            data_str = str(data)
        
        # Skip encryption for empty strings
        if not data_str.strip():
            return ''
        
        # Generate encryption key
        fernet_key = _generate_key(key)
        fernet = Fernet(fernet_key)
        
        # Add metadata for verification
        metadata = {
            'data': data_str,
            'timestamp': datetime.utcnow().isoformat(),
            'type': type(data).__name__
        }
        
        # Encrypt the data with metadata
        plaintext = json.dumps(metadata, ensure_ascii=False)
        encrypted_bytes = fernet.encrypt(plaintext.encode('utf-8'))
        
        # Return base64 encoded string
        return base64.b64encode(encrypted_bytes).decode('ascii')
        
    except Exception as e:
        logger.error(f"Encryption failed: {str(e)}")
        raise EncryptionError(f"Failed to encrypt data: {str(e)}")

def decrypt_data(encrypted_data: str, key: Optional[str] = None) -> Optional[str]:
    """Decrypt given data using Fernet decryption with improved security
    
    Args:
        encrypted_data: Base64 encoded encrypted data
        key: Decryption key (optional, will use default from settings)
        
    Returns:
        str: Decrypted data or None if decryption fails
        
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
            logger.warning("Data appears to be unencrypted, returning as-is")
            return encrypted_data
        
        # Decode from base64
        encrypted_bytes = base64.b64decode(encrypted_data.encode('ascii'))
        
        # Generate decryption key
        fernet_key = _generate_key(key)
        fernet = Fernet(fernet_key)
        
        # Decrypt the data
        decrypted_bytes = fernet.decrypt(encrypted_bytes)
        decrypted_str = decrypted_bytes.decode('utf-8')
        
        # Parse metadata if present
        try:
            metadata = json.loads(decrypted_str)
            if isinstance(metadata, dict) and 'data' in metadata:
                return metadata['data']
            else:
                # Legacy format without metadata
                return decrypted_str
        except json.JSONDecodeError:
            # Legacy format without metadata
            return decrypted_str
            
    except (InvalidToken, base64.binascii.Error, ValueError) as e:
        logger.warning(f"Decryption failed, data might be corrupted or key is invalid: {str(e)}")
        raise DecryptionError(f"Failed to decrypt data: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected decryption error: {str(e)}")
        raise DecryptionError(f"Failed to decrypt data: {str(e)}")

def _is_encrypted_data(data: str) -> bool:
    """Check if data appears to be encrypted based on format
    
    Args:
        data: String to check
        
    Returns:
        bool: True if data appears to be encrypted
    """
    if not data:
        return False
    
    try:
        # Check if it's valid base64
        base64.b64decode(data.encode('ascii'))
        # If it's longer than typical plaintext and contains base64 chars
        return len(data) > 50 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in data)
    except:
        return False

def encrypt_dict(data_dict: dict, fields_to_encrypt: list, key: Optional[str] = None) -> dict:
    """Encrypt specific fields in a dictionary
    
    Args:
        data_dict: Dictionary containing data
        fields_to_encrypt: List of field names to encrypt
        key: Encryption key (optional)
        
    Returns:
        dict: Dictionary with specified fields encrypted
    """
    if not isinstance(data_dict, dict):
        raise ValueError("data_dict must be a dictionary")
    
    result = data_dict.copy()
    
    for field in fields_to_encrypt:
        if field in result and result[field] is not None:
            try:
                result[field] = encrypt_data(result[field], key)
            except EncryptionError as e:
                logger.error(f"Failed to encrypt field '{field}': {str(e)}")
                # Keep original value if encryption fails
                pass
    
    return result

def decrypt_dict(data_dict: dict, fields_to_decrypt: list, key: Optional[str] = None) -> dict:
    """Decrypt specific fields in a dictionary
    
    Args:
        data_dict: Dictionary containing encrypted data
        fields_to_decrypt: List of field names to decrypt
        key: Decryption key (optional)
        
    Returns:
        dict: Dictionary with specified fields decrypted
    """
    if not isinstance(data_dict, dict):
        raise ValueError("data_dict must be a dictionary")
    
    result = data_dict.copy()
    
    for field in fields_to_decrypt:
        if field in result and result[field] is not None:
            try:
                decrypted = decrypt_data(result[field], key)
                if decrypted is not None:
                    result[field] = decrypted
            except DecryptionError as e:
                logger.error(f"Failed to decrypt field '{field}': {str(e)}")
                # Keep original value if decryption fails
                pass
    
    return result

def is_encryption_enabled() -> bool:
    """Check if encryption is properly configured
    
    Returns:
        bool: True if encryption is enabled and configured
    """
    key = _get_encryption_key()
    return key != 'default-key-change-this-in-production'

def generate_encryption_key() -> str:
    """Generate a new secure encryption key
    
    Returns:
        str: New encryption key
    """
    return base64.urlsafe_b64encode(os.urandom(32)).decode('ascii')
