from cryptography.fernet import Fernet
from django.conf import settings

def get_fernet_instance():
    """Returns a Fernet instance using the key from settings."""
    key = settings.ENCRYPTION_KEY
    return Fernet(key.encode())

def encrypt_message(text):
    """Encrypts a plaintext string and returns a base64 encoded string."""
    if not text:
        return ""
    f = get_fernet_instance()
    encrypted_bytes = f.encrypt(text.encode('utf-8'))
    return encrypted_bytes.decode('utf-8')

def decrypt_message(cipher_text):
    """Decrypts a base64 encoded encrypted string and returns the plaintext."""
    if not cipher_text:
        return ""
    f = get_fernet_instance()
    try:
        decrypted_bytes = f.decrypt(cipher_text.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        return "[Message could not be decrypted]"
