from django.contrib import admin

from .models import QRCode


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    """Admin interface for QR codes."""

    list_display = ("id", "uuid", "house", "is_claimed", "created_at")
    list_filter = ("created_at",)
    search_fields = ("uuid", "house__address", "house__house_number")
    readonly_fields = ("uuid", "created_at", "qr_url_display")

    def is_claimed(self, obj):
        """Check if QR code is claimed."""
        return bool(obj.house and obj.house.owner)

    is_claimed.boolean = True
    is_claimed.short_description = "Claimed"

    def qr_url_display(self, obj):
        """Display QR URL."""
        return obj.get_qr_url()

    qr_url_display.short_description = "QR URL"
