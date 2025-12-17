import uuid
import qrcode
from io import BytesIO

from django.db import models
from django.core.files import File

from apps.houses.models import House


class QRCode(models.Model):
    id = models.CharField(
        max_length=16,
        primary_key=True,
        editable=False
    )

    house = models.OneToOneField(
        House,
        on_delete=models.CASCADE,
        related_name="qr_code"
    )

    image = models.ImageField(
        upload_to="qr_codes/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = uuid.uuid4().hex[:16]
        super().save(*args, **kwargs)

        if not self.image:
            self.generate_qr_image()

    def generate_qr_image(self):
        qr = qrcode.make(self.id)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        self.image.save(
            f"{self.id}.png",
            File(buffer),
            save=True
        )

    def __str__(self):
        return self.id
