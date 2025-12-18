import uuid
from django.db import models
from ..users.models import User
from ..regions.models import Mahalla


class House(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="houses", verbose_name="Owner"
    )

    mahalla = models.ForeignKey(
        Mahalla, on_delete=models.CASCADE, related_name="houses", verbose_name="Neighborhood"
    )

    house_number = models.CharField(max_length=50, verbose_name="House number", blank=True)
    address = models.CharField(max_length=255, verbose_name="Address")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")

    class Meta:
        verbose_name = "House"
        verbose_name_plural = "Houses"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.address} ({self.mahalla.name})"
