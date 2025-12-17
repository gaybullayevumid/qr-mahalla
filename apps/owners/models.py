from django.db import models
from ..users.models import User
from ..regions.models import Mahalla


class OwnerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="owner_profile"
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)

    # Manzil
    mahalla = models.ForeignKey(
        Mahalla,
        on_delete=models.PROTECT,
        related_name="owners"
    )
    address = models.CharField(
        max_length=255,
        help_text="Ko‘cha, uy raqami"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
