import uuid
import qrcode
from io import BytesIO

from django.db import models
from django.core.files import File
from django.conf import settings

from apps.houses.models import House
from apps.utils import GapFillingIDMixin


class QRCode(GapFillingIDMixin, models.Model):
    uuid = models.CharField(
        max_length=16, unique=True, editable=False, verbose_name="UUID"
    )

    house = models.OneToOneField(
        House, on_delete=models.CASCADE, related_name="qr_code", verbose_name="House"
    )

    image = models.ImageField(
        upload_to="qr_codes/", blank=True, null=True, verbose_name="QR code image"
    )

    is_delivered = models.BooleanField(
        default=False, verbose_name="Is delivered to house owner"
    )

    delivered_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Delivered at"
    )

    delivered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delivered_qrcodes",
        verbose_name="Delivered by",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")

    class Meta:
        verbose_name = "QR Code"
        verbose_name_plural = "QR Codes"
        ordering = ["id"]

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4().hex[:16]

        super().save(*args, **kwargs)

        if not self.image:
            self.generate_qr_image()

    def generate_qr_image(self):
        qr = qrcode.make(self.uuid)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        self.image.save(f"{self.uuid}.png", File(buffer), save=True)

    def __str__(self):
        return f"QR #{self.id} - {self.uuid}"
