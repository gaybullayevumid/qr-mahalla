import uuid
from django.db import models
from ..users.models import User
from ..regions.models import Mahalla


class House(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="houses"
    )

    mahalla = models.ForeignKey(
        Mahalla,
        on_delete=models.CASCADE,
        related_name="houses"
    )

    address = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.address} ({self.mahalla.name})"
