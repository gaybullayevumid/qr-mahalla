import uuid
import qrcode
from io import BytesIO
from typing import Optional

from django.db import models
from django.core.files import File
from django.conf import settings

from apps.houses.models import House
from apps.utils import GapFillingIDMixin


class QRCode(GapFillingIDMixin, models.Model):
    """
    QR code for house identification and ownership claiming.

    Each QR code has a unique 16-character UUID and can be linked to a house.
    Generates Telegram bot URL for easy scanning.
    """

    uuid = models.CharField(
        max_length=16, unique=True, editable=False, verbose_name="UUID"
    )

    house = models.OneToOneField(
        House,
        on_delete=models.CASCADE,
        related_name="qr_code",
        verbose_name="House",
        null=True,
        blank=True,
    )

    image = models.ImageField(
        upload_to="qr_codes/", blank=True, null=True, verbose_name="QR code image"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")

    class Meta:
        verbose_name = "QR Code"
        verbose_name_plural = "QR Codes"
        ordering = ["id"]

    def save(self, *args, **kwargs) -> None:
        """Generate UUID if not exists before saving."""
        if not self.uuid:
            self.uuid = uuid.uuid4().hex[:16]

        # Don't call generate_qr_image() here to avoid nested saves
        # Image will be generated later if needed
        super().save(*args, **kwargs)

    def get_qr_url(self) -> str:
        """
        Get Telegram bot URL with QR code ID.

        Format: https://t.me/{bot_username}/start?startapp=QR_KEY_{uuid}

        Returns:
            Full Telegram bot URL string
        """
        bot_username = getattr(settings, "TELEGRAM_BOT_USERNAME", "qrmahallabot")
        return f"https://t.me/{bot_username}/start?startapp=QR_KEY_{self.uuid}"

    def generate_qr_image(self) -> None:
        """
        Generate QR code image with Telegram bot URL.

        Only generates if image doesn't exist yet.
        Saves image to media/qr_codes/ directory.
        """
        if self.image:  # Don't regenerate if image exists
            return

        # Generate QR code with Telegram bot URL
        qr_url = self.get_qr_url()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)  # Reset buffer position to beginning
        self.image.save(f"{self.uuid}.png", File(buffer), save=False)

    def __str__(self) -> str:
        """String representation of QR code."""
        return f"QR #{self.id} - {self.uuid}"
