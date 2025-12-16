import string
import random
from django.db import models
from ..users.models import User

# 16 belgili noyob ID generatsiyasi
def generate_16_char_id():
    chars = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return ''.join(random.choices(chars, k=16))

class QRCode(models.Model):
    OBJECT_TYPES = (
        ('house', 'Uy'),
        ('car', 'Mashina'),
        ('other', 'Boshqa'),
    )

    id = models.CharField(
        primary_key=True,
        max_length=16,
        default=generate_16_char_id,
        editable=False
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='qrcodes')
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id

class ScanLog(models.Model):
    qr = models.ForeignKey(QRCode, on_delete=models.CASCADE)
    scanned_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )
    scanned_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
