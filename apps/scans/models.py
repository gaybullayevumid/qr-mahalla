from django.db import models
from apps.qrcodes.models import QRCode
from apps.users.models import User


class ScanLog(models.Model):
    qr = models.ForeignKey(QRCode, on_delete=models.CASCADE)
    scanned_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    scanned_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.qr.id} scanned"
