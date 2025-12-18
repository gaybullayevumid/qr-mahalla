import random
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("super_admin", "Super Admin"),
        ("government", "Davlat xodimi"),
        ("mahalla_admin", "Mahalla boshlig‘i"),
        ("owner", "Uy egasi"),
        ("user", "Oddiy foydalanuvchi"),
    )

    phone = models.CharField(max_length=15, unique=True, verbose_name="Telefon raqam")

    first_name = models.CharField(max_length=100, blank=True, verbose_name="Ism")
    last_name = models.CharField(max_length=100, blank=True, verbose_name="Familiya")
    passport_id = models.CharField(
        max_length=20, blank=True, verbose_name="Pasport seriya"
    )
    address = models.TextField(blank=True, verbose_name="Manzil")

    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default="user", verbose_name="Rol"
    )

    is_active = models.BooleanField(default=True, verbose_name="Faol")
    is_verified = models.BooleanField(default=False, verbose_name="Tasdiqlangan")
    is_staff = models.BooleanField(default=False, verbose_name="Xodim")

    date_joined = models.DateTimeField(
        auto_now_add=True, verbose_name="Ro'yxatdan o'tgan sana"
    )

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.phone


class PhoneOTP(models.Model):
    phone = models.CharField(max_length=15, verbose_name="Telefon raqam")
    code = models.CharField(max_length=6, verbose_name="Kod")
    is_used = models.BooleanField(default=False, verbose_name="Ishlatilgan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

    class Meta:
        verbose_name = "SMS kod"
        verbose_name_plural = "SMS kodlar"
        ordering = ["-created_at"]

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=2)

    @staticmethod
    def generate_code():
        return str(random.randint(100000, 999999))

    def __str__(self):
        return f"{self.phone} - {self.code}"
