import uuid
import random
from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("Phone is required")

        user = self.model(phone=phone, **extra_fields)

        if password:
            user.set_password(password)   # ✅ agar parol bo‘lsa
        else:
            user.set_unusable_password()  # OTP userlar uchun

        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not password:
            raise ValueError("Superuser must have a password")

        return self.create_user(phone, password, **extra_fields)



class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('owner', 'Uy egasi'),
        ('government', 'Davlat xodimi'),
        ('user', 'Oddiy foydalanuvchi'),
    )

    phone = models.CharField(max_length=20, unique=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user'
    )

    # Uy egasiga tegishli ma’lumotlar
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    father_name = models.CharField(max_length=100, blank=True)

    address = models.TextField(blank=True)
    passport_id = models.CharField(max_length=20, blank=True)

    # Texnik maydonlar
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone


class OTP(models.Model):
    phone = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    @staticmethod
    def generate_code():
        return str(random.randint(100000, 999999))

    def __str__(self):
        return f"{self.phone} - {self.code}"


class QRCode(models.Model):
    OBJECT_TYPES = (
        ('house', 'Uy'),
        ('car', 'Mashina'),
        ('other', 'Boshqa'),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='qrcodes'
    )

    object_type = models.CharField(
        max_length=20,
        choices=OBJECT_TYPES,
        default='house'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"QR {self.id} - {self.owner.phone}"


class ScanLog(models.Model):
    qr = models.ForeignKey(
        QRCode,
        on_delete=models.CASCADE,
        related_name='scans'
    )

    scanned_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    scanned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scan {self.qr.id} at {self.scanned_at}"


