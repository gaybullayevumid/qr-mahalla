from django.db import models


class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class District(models.Model):
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, related_name="districts"
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.region.name})"


class Mahalla(models.Model):
    district = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name="mahallas"
    )
    name = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.name} ({self.district.name})"
