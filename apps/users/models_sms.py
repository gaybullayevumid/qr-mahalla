import uuid
from django.db import models
from django.utils import timezone


class SMSLog(models.Model):
    """
    SMS yuborilgan xabarlarni kuzatish uchun model.

    Bu model barcha yuborilgan SMS xabarlarini saqlaydi va
    SMS xizmatining ishlashini monitoring qilish imkonini beradi.
    """

    SMS_TYPE_CHOICES = (
        ("verification", "Tasdiqlash kodi"),
        ("registration", "Ro'yxatdan o'tish"),
        ("qr_scan", "QR kod skaner"),
        ("notification", "Bildirishnoma"),
    )

    STATUS_CHOICES = (
        ("pending", "Kutilmoqda"),
        ("sent", "Yuborildi"),
        ("failed", "Xato"),
        ("delivered", "Yetkazildi"),
    )

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID"
    )

    phone = models.CharField(
        max_length=15, verbose_name="Telefon raqami", db_index=True
    )

    message = models.TextField(verbose_name="SMS matni")

    sms_type = models.CharField(
        max_length=20,
        choices=SMS_TYPE_CHOICES,
        default="notification",
        verbose_name="SMS turi",
        db_index=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Status",
        db_index=True,
    )

    user = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sms_logs",
        verbose_name="Foydalanuvchi",
    )

    error_message = models.TextField(blank=True, null=True, verbose_name="Xato xabari")

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Yaratilgan vaqti", db_index=True
    )

    sent_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Yuborilgan vaqti"
    )

    # Eskiz API response data
    eskiz_response = models.JSONField(
        null=True, blank=True, verbose_name="Eskiz API javobi"
    )

    class Meta:
        verbose_name = "SMS Log"
        verbose_name_plural = "SMS Logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at", "status"]),
            models.Index(fields=["phone", "-created_at"]),
            models.Index(fields=["sms_type", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.phone} - {self.get_sms_type_display()} - {self.status}"

    def mark_as_sent(self, response_data=None):
        """SMS muvaffaqiyatli yuborilganda chaqiriladi"""
        self.status = "sent"
        self.sent_at = timezone.now()
        if response_data:
            self.eskiz_response = response_data
        self.save(update_fields=["status", "sent_at", "eskiz_response"])

    def mark_as_failed(self, error_msg):
        """SMS yuborishda xato bo'lganda chaqiriladi"""
        self.status = "failed"
        self.error_message = error_msg
        self.save(update_fields=["status", "error_message"])
