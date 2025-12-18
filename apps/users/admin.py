from django.contrib import admin
from .models import User, PhoneOTP, UserSession


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("phone", "role", "is_verified", "is_active")
    list_filter = ("role", "is_verified")
    search_fields = ("phone",)


@admin.register(PhoneOTP)
class PhoneOTPAdmin(admin.ModelAdmin):
    list_display = ("phone", "code", "is_used", "created_at")


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "device_name",
        "device_id",
        "ip_address",
        "is_active",
        "last_activity",
        "created_at",
    ]
    list_filter = ["is_active", "created_at"]
    search_fields = ["user__phone", "device_id", "device_name"]
    readonly_fields = ["created_at", "last_activity"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")
