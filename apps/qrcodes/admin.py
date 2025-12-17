from django.contrib import admin
from django.utils.html import format_html
from .models import QRCode


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'qr_preview', 'created_at')
    readonly_fields = ('qr_preview',)

    def qr_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="120" height="120" />',
                obj.image.url
            )
        return "No QR"

    qr_preview.short_description = "QR Code"
