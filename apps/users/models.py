import random
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.conf import settings
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


class UserSession(models.Model):
    """Track user sessions across devices"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name="User",
    )
    device_id = models.CharField(
        max_length=255,
        verbose_name="Device ID",
        help_text="Unique device identifier from frontend",
    )
    device_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Device Name",
        help_text="e.g., iPhone 13, Samsung Galaxy",
    )
    refresh_token = models.TextField(
        verbose_name="Refresh Token", help_text="JWT refresh token"
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name="IP Address"
    )
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    last_activity = models.DateTimeField(auto_now=True, verbose_name="Last Activity")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "User Session"
        verbose_name_plural = "User Sessions"
        ordering = ["-last_activity"]
        unique_together = ["user", "device_id"]

    def __str__(self):
        return f"{self.user.phone} - {self.device_name or self.device_id}"
