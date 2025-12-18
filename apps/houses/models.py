import uuid
from django.db import models
from ..users.models import User
from ..regions.models import Mahalla


class House(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="houses", verbose_name="Uy egasi"
    )

    mahalla = models.ForeignKey(
        Mahalla, on_delete=models.CASCADE, related_name="houses", verbose_name="Mahalla"
    )

    address = models.CharField(max_length=255, verbose_name="Manzil")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

    class Meta:
        verbose_name = "Uy"
        verbose_name_plural = "Uylar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.address} ({self.mahalla.name})"
