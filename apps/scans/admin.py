from django.contrib import admin
from .models import ScanLog


@admin.register(ScanLog)
class ScanLogAdmin(admin.ModelAdmin):
    list_display = ("qr", "scanned_by", "scanned_at", "ip_address")
