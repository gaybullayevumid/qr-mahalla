import json
from cryptography.fernet import Fernet
from django.conf import settings

fernet = Fernet(settings.QR_SECRET_KEY)


def encrypt_owner_data(data: dict) -> str:
    json_data = json.dumps(data)
    encrypted = fernet.encrypt(json_data.encode())
    return encrypted.decode()


def decrypt_owner_data(token: str) -> dict:
    decrypted = fernet.decrypt(token.encode())
    return json.loads(decrypted.decode())
