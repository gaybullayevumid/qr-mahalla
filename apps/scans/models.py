from django.db import models
from apps.qrcodes.models import QRCode
from apps.users.models import User


class ScanLog(models.Model):
    qr = models.ForeignKey(QRCode, on_delete=models.CASCADE, verbose_name="QR kod")
    scanned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Skanerlagan foydalanuvchi",
    )
    scanned_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Skanerlangan vaqt"
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name="IP manzil"
    )

    class Meta:
        verbose_name = "Skanerlash tarixi"
        verbose_name_plural = "Skanerlash tarixi"
        ordering = ["-scanned_at"]

    def __str__(self):
        return f"{self.qr.id} scanned"
