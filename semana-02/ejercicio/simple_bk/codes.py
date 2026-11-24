import hashlib
import base64
from cryptography.fernet import Fernet
from config import CRIPTO_SECRET_KEY


def derive_key(secret: str) -> bytes:
    hashed = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(hashed)


def encrypt(message: str) -> str:
    fernet_key = derive_key(CRIPTO_SECRET_KEY)
    cipher = Fernet(fernet_key)

    encrypted = cipher.encrypt(message.encode())
    return encrypted.decode()


def decrypt(encrypted_message: str, key: str) -> str:
    # Usa la clave que entrega quien llama, no la constante del módulo.
    fernet_key = derive_key(key)
    cipher = Fernet(fernet_key)

    decrypted = cipher.decrypt(encrypted_message.encode())
    return decrypted.decode()
