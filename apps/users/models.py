import random
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("super_admin", "Super Admin"),
        ("government", "Government Officer"),
        ("mahalla_admin", "Neighborhood Admin"),
        ("owner", "House Owner"),
        ("user", "Regular User"),
    )

    phone = models.CharField(max_length=15, unique=True, verbose_name="Phone number")

    first_name = models.CharField(max_length=100, blank=True, verbose_name="First name")
    last_name = models.CharField(max_length=100, blank=True, verbose_name="Last name")
    passport_id = models.CharField(
        max_length=20, blank=True, verbose_name="Passport ID"
    )
    address = models.TextField(blank=True, verbose_name="Address")

    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default="user", verbose_name="Role"
    )

    is_active = models.BooleanField(default=True, verbose_name="Active")
    is_verified = models.BooleanField(default=False, verbose_name="Verified")
    is_staff = models.BooleanField(default=False, verbose_name="Staff")

    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Date joined")

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.phone


class PhoneOTP(models.Model):
    phone = models.CharField(max_length=15, verbose_name="Phone number")
    code = models.CharField(max_length=6, verbose_name="Code")
    is_used = models.BooleanField(default=False, verbose_name="Used")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")

    class Meta:
        verbose_name = "SMS Code"
        verbose_name_plural = "SMS Codes"
        ordering = ["-created_at"]

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=2)

    @staticmethod
    def generate_code():
        return str(random.randint(100000, 999999))

    def __str__(self):
        return f"{self.phone} - {self.code}"
