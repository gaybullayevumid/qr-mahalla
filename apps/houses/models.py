import uuid
from django.db import models
from apps.utils import GapFillingIDMixin
from ..users.models import User
from ..regions.models import Mahalla


class House(GapFillingIDMixin, models.Model):
    """Model representing a house or residential property.

    A house belongs to a mahalla (neighborhood) and can have an owner.
    """

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="houses",
        verbose_name="Owner",
        null=True,
        blank=True,
    )

    mahalla = models.ForeignKey(
        Mahalla,
        on_delete=models.CASCADE,
        related_name="houses",
        verbose_name="Neighborhood",
    )

    house_number = models.CharField(
        max_length=50, verbose_name="House number", blank=True
    )
    address = models.CharField(max_length=255, verbose_name="Address")

    created_by_agent = models.BooleanField(
        default=False, verbose_name="Created by agent"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")

    class Meta:
        verbose_name = "House"
        verbose_name_plural = "Houses"
        ordering = ["-created_at"]

    def __str__(self):
        owner_name = self.owner.phone if self.owner else "No owner"
        return f"{self.address} ({self.mahalla.name}) - {owner_name}"
