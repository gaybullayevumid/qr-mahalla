from django.contrib import admin
from .models import User, PhoneOTP


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("phone", "role", "is_verified", "is_active")
    list_filter = ("role", "is_verified")
    search_fields = ("phone",)


@admin.register(PhoneOTP)
class PhoneOTPAdmin(admin.ModelAdmin):
    list_display = ("phone", "code", "is_used", "created_at")
