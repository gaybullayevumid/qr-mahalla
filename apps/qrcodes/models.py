import uuid
import qrcode
from io import BytesIO

from django.db import models
from django.core.files import File

from apps.houses.models import House
from apps.utils import GapFillingIDMixin


class QRCode(GapFillingIDMixin, models.Model):
    """QR code for house identification and ownership claiming"""

    uuid = models.CharField(
        max_length=16, unique=True, editable=False, verbose_name="UUID"
    )

    house = models.OneToOneField(
        House, on_delete=models.CASCADE, related_name="qr_code", verbose_name="House"
    )

    image = models.ImageField(
        upload_to="qr_codes/", blank=True, null=True, verbose_name="QR code image"
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
        """Generate QR code image from UUID"""
        qr = qrcode.make(self.uuid)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        self.image.save(f"{self.uuid}.png", File(buffer), save=True)

    def __str__(self):
        return f"QR #{self.id} - {self.uuid}"
