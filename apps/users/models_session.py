from django.db import models
from django.conf import settings


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
