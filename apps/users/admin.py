from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTP, QRCode, ScanLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'phone', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active')
    search_fields = ('phone',)
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('phone',)}),
        ('Personal info', {
            'fields': (
                'first_name',
                'last_name',
                'father_name',
                'address',
                'passport_id',
            )
        }),
        ('Permissions', {
            'fields': (
                'role',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'role'),
        }),
    )

    filter_horizontal = ()
