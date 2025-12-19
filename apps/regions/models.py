from django.db import models
from apps.utils import GapFillingIDMixin
from apps.users.models import User


class Region(GapFillingIDMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name="Region name")

    class Meta:
        verbose_name = "Region"
        verbose_name_plural = "Regions"
        ordering = ["name"]

    def __str__(self):
        return self.name


class District(GapFillingIDMixin, models.Model):
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name="districts",
        verbose_name="Region",
    )
    name = models.CharField(max_length=100, verbose_name="District name")

    class Meta:
        verbose_name = "District"
        verbose_name_plural = "Districts"
        ordering = ["region", "name"]

    def __str__(self):
        return f"{self.region.name} - {self.name}"


class Mahalla(GapFillingIDMixin, models.Model):
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name="mahallas",
        verbose_name="District",
    )
    name = models.CharField(max_length=100, verbose_name="Neighborhood name")

    # neighborhood admin
    admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_mahallas",
        verbose_name="Neighborhood admin",
    )

    class Meta:
        verbose_name = "Neighborhood"
        verbose_name_plural = "Neighborhoods"
        ordering = ["district", "name"]

    def __str__(self):
        return f"{self.district.name} - {self.name}"
