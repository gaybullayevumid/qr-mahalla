import uuid
import qrcode
from io import BytesIO

from django.db import models
from django.core.files import File

from apps.users.models import User
from .utils import encrypt_owner_data


class QRCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="qr_code")

    image = models.ImageField(upload_to="qr_codes/", blank=True, null=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    def generate_qr_image(self):
        """
        QR ichiga uy egasining TO‘LIQ ma’lumotlari
        SHIFRLANGAN holatda joylanadi
        """

        owner = self.owner

        owner_data = {
            "owner_id": owner.id,
            "first_name": owner.first_name,
            "last_name": owner.last_name,
            "father_name": owner.father_name,
            "phone": owner.phone,
            "address": owner.address,
            "passport_id": owner.passport_id,
        }

        encrypted_payload = encrypt_owner_data(owner_data)

        qr = qrcode.make(encrypted_payload)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        file_name = f"qr_{self.id}.png"
        self.image.save(file_name, File(buffer), save=False)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)

        # faqat yangi yaratilganda QR generatsiya qilinadi
        if is_new and not self.image:
            self.generate_qr_image()
            super().save(update_fields=["image"])
