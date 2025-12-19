from django.db import models
from apps.utils import GapFillingIDMixin
from apps.qrcodes.models import QRCode
from apps.users.models import User


class ScanLog(GapFillingIDMixin, models.Model):
    qr = models.ForeignKey(QRCode, on_delete=models.CASCADE, verbose_name="QR Code")
    scanned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Scanned by",
    )
    scanned_at = models.DateTimeField(auto_now_add=True, verbose_name="Scanned at")
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name="IP address"
    )

    class Meta:
        verbose_name = "Scan Log"
        verbose_name_plural = "Scan Logs"
        ordering = ["-scanned_at"]

    def __str__(self):
        return f"{self.qr.id} scanned"
