from django.db import models
from apps.users.models import User


class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class District(models.Model):
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name="districts"
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.region.name} - {self.name}"


class Mahalla(models.Model):
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name="mahallas"
    )
    name = models.CharField(max_length=100)

    # mahalla boshlig‘i
    admin = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mahalla"
    )

    def __str__(self):
        return f"{self.district.name} - {self.name}"
