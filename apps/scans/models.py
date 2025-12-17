from django.db import models
from apps.qrcodes.models import QRCode
from apps.users.models import User


class ScanLog(models.Model):
    qr = models.ForeignKey(
        QRCode,
        on_delete=models.CASCADE,
        related_name="scans"
    )

    scanned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scan_logs"
    )

    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.qr.id} - {self.created_at}"
