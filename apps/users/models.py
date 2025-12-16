from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('owner', 'Uy egasi'),
        ('government', 'Davlat xodimi'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    phone = models.CharField(max_length=20, blank=True)
    passport_id = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    father_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.username
