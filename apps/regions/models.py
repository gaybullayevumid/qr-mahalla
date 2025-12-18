from django.db import models
from apps.users.models import User


class Region(models.Model):
    name = models.CharField(max_length=100, verbose_name="Viloyat nomi")

    class Meta:
        verbose_name = "Viloyat"
        verbose_name_plural = "Viloyatlar"
        ordering = ["name"]

    def __str__(self):
        return self.name


class District(models.Model):
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name="districts",
        verbose_name="Viloyat",
    )
    name = models.CharField(max_length=100, verbose_name="Tuman nomi")

    class Meta:
        verbose_name = "Tuman"
        verbose_name_plural = "Tumanlar"
        ordering = ["region", "name"]

    def __str__(self):
        return f"{self.region.name} - {self.name}"


class Mahalla(models.Model):
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name="mahallas",
        verbose_name="Tuman",
    )
    name = models.CharField(max_length=100, verbose_name="Mahalla nomi")

    # mahalla boshlig'i
    admin = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mahalla",
        verbose_name="Mahalla boshlig'i",
    )

    class Meta:
        verbose_name = "Mahalla"
        verbose_name_plural = "Mahallalar"
        ordering = ["district", "name"]

    def __str__(self):
        return f"{self.district.name} - {self.name}"
