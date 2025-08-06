# Django Model Field Encryption System

This document describes the new, streamlined encryption system implemented in `utils/encryption.py`.

## Overview

The encryption system provides automatic encryption/decryption of sensitive Django model fields using Fernet symmetric encryption with PBKDF2 key derivation.

## Key Features

- **Single File Solution**: All encryption logic consolidated in `utils/encryption.py`
- **Automatic Encryption**: Fields are encrypted before saving to database
- **Transparent Decryption**: Fields are decrypted when accessed through model methods
- **Double Encryption Prevention**: Automatically detects and prevents re-encryption of already encrypted data
- **Caching**: Decrypted values are cached for performance
- **Migration Tools**: Built-in tools to fix corrupted/multi-encrypted data
- **Validation**: Built-in tools to test and validate the encryption system

## Components

### Core Functions

- `encrypt_data(data, key=None)` - Encrypt any data type
- `decrypt_data(encrypted_data, key=None)` - Decrypt data
- `_is_encrypted_data(data)` - Check if data appears to be encrypted

### Django Integration

- `EncryptedFieldMixin` - Mixin for Django models with encrypted fields
- `EncryptedCharField` - Custom Django field with automatic encryption/decryption

### Utility Functions

- `encrypt_dict()` / `decrypt_dict()` - Bulk operations on dictionaries
- `test_encryption_roundtrip()` - Test basic encryption functionality
- `validate_encryption_setup()` - Validate system configuration
- `fix_multiple_encrypted_data()` - Fix corrupted data

## Usage

### 1. Model Integration

```python
from utils.encryption import EncryptedFieldMixin

class UserProfile(EncryptedFieldMixin, models.Model):
    # Define which fields should be encrypted
    ENCRYPTED_FIELDS = ['phone_number', 'address', 'bio']
    
    phone_number = models.CharField(max_length=500, blank=True)  # Increased for encryption
    address = models.TextField(blank=True)
    bio = models.TextField(max_length=1000, blank=True)
    # ... other fields
```

### 2. Accessing Encrypted Data

```python
# Get user profile
profile = UserProfile.objects.get(user=user)

# Access decrypted data
phone = profile.get_decrypted_field('phone_number')
address = profile.get_decrypted_field('address')

# Get all decrypted fields at once
decrypted_data = profile.get_all_decrypted_fields()
# Returns: {'phone_number': '+1234567890', 'address': '123 Main St', 'bio': 'Hello world'}

# Set new field values
profile.set_field_value('phone_number', '+1-555-123-4567')
profile.save()  # Automatically encrypted before saving
```

### 3. Using Custom Encrypted Field

```python
from utils.encryption import EncryptedCharField

class MyModel(models.Model):
    sensitive_data = EncryptedCharField(max_length=500)
    # This field will automatically encrypt/decrypt data
```

### 4. Management Commands

```bash
# Test basic encryption functionality
python manage.py test_encryption --test-basic

# Validate all encrypted data in database
python manage.py test_encryption --validate-all

# Fix corrupted/multi-encrypted data
python manage.py test_encryption --fix-corrupted

# Run all tests
python manage.py test_encryption --test-basic --validate-all
```

## Configuration

### Settings

Add to your Django settings:

```python
# Required: Encryption key for sensitive data
ENCRYPTION_KEY = 'your-secure-encryption-key-here'
```

**Important**: 
- Use a strong, randomly generated key in production
- Store the key securely (environment variables, secrets manager)
- Never commit the key to version control
- Changing the key will make existing encrypted data unreadable

### Generate Secure Key

```python
from utils.encryption import generate_encryption_key
key = generate_encryption_key()
print(f"ENCRYPTION_KEY={key}")
```

## Security Features

- **PBKDF2 Key Derivation**: 100,000 iterations with SHA-256
- **Fernet Encryption**: Authenticated encryption with timestamp verification
- **Base64 Encoding**: Safe storage in text database fields
- **Automatic Key Management**: Consistent key derivation from master key
- **No Metadata Storage**: Simple encryption without complex metadata (prevents corruption)

## Database Considerations

### Field Size Requirements

Encrypted data is typically 3-4x larger than original data due to:
- Base64 encoding overhead (~33%)
- Fernet encryption overhead (fixed ~60 bytes)
- PBKDF2 salt and metadata

**Recommendation**: Set `max_length=500` for encrypted CharField fields.

### Indexing and Queries

- Encrypted fields cannot be efficiently queried or indexed
- Use separate non-encrypted fields for searching/filtering
- Consider using hash fields for exact match queries

## Troubleshooting

### Common Issues

1. **"Data appears to be unencrypted" warnings**
   - Normal for data that hasn't been encrypted yet
   - Run migration to encrypt existing data

2. **Decryption failures**
   - Check if encryption key has changed
   - Verify data hasn't been corrupted
   - Use management command to validate data

3. **Double encryption**
   - Should be prevented automatically
   - If it occurs, use `--fix-corrupted` command

### Validation Commands

```bash
# Check system status
python manage.py test_encryption

# Detailed validation
python manage.py test_encryption --validate-all

# Fix issues
python manage.py test_encryption --fix-corrupted
```

## Migration from Old System

If migrating from the previous `encryption_mixins.py` system:

1. The new system is backward compatible
2. Run `python manage.py test_encryption --fix-corrupted` to fix any multi-encrypted data
3. Update imports from `utils.encryption_mixins` to `utils.encryption`
4. Test thoroughly with `--validate-all`

## Best Practices

1. **Always backup data** before running encryption fixes
2. **Test in development** before applying to production
3. **Monitor encryption logs** for warnings/errors
4. **Use separate search fields** for encrypted data that needs to be queried
5. **Regular validation** using management commands
6. **Secure key storage** using environment variables or secrets management

## Performance Considerations

- Decryption is cached per model instance
- Cache is cleared on `refresh_from_db()`
- Consider loading patterns for encrypted fields
- Use `get_all_decrypted_fields()` for bulk access

## Example Complete Model

```python
from django.db import models
from utils.encryption import EncryptedFieldMixin

class UserProfile(EncryptedFieldMixin, models.Model):
    ENCRYPTED_FIELDS = ['phone_number', 'address', 'bio', 'ssn']
    
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    
    # Encrypted fields (increased max_length for encryption overhead)
    phone_number = models.CharField(max_length=500, blank=True)
    address = models.TextField(blank=True)
    bio = models.TextField(max_length=2000, blank=True)
    ssn = models.CharField(max_length=500, blank=True)
    
    # Non-encrypted fields for searching/filtering
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def phone_display(self):
        """Get formatted phone number for display"""
        return self.get_decrypted_field('phone_number')
    
    def update_contact_info(self, phone, address):
        """Update encrypted contact information"""
        self.set_field_value('phone_number', phone)
        self.set_field_value('address', address)
        self.save()
```

This encryption system provides robust, transparent protection for sensitive data while maintaining ease of use and good performance.
