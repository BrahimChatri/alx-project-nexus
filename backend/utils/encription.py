from cryptography.fernet import Fernet, InvalidToken
import base64
import hashlib

def _generate_key(key: str) -> bytes:
    """Generate a Fernet key based on the provided key"""
    digest = hashlib.sha256(key.encode()).digest()
    return base64.urlsafe_b64encode(digest)

def encrypt_data(data: str | dict | list, key: str = None) -> str:
    """Encrypt given data using a key"""
    if key is None:
        from django.conf import settings
        key = getattr(settings, 'ENCRYPTION_KEY', 'default-key-change-this')
    
    if isinstance(data, (dict, list)):
        import json
        data = json.dumps(data)

    fernet_key = _generate_key(key)
    fernet = Fernet(fernet_key)
    encrypted: bytes = fernet.encrypt(data.encode())
    return encrypted.decode()


def decrypt_data(data: str, key: str):
    """Decrypt given data using a key"""
    try :
        fernet_key = _generate_key(key)
        fernet = Fernet(fernet_key)
        decrypted = fernet.decrypt(data.encode()).decode()
        return decrypted
    except (InvalidToken, base64.binascii.Error):
        # Decryption failed (data was not encrypted properly)
        print("[Warning] Data is not encrypted or key is invalid.")
        return None
