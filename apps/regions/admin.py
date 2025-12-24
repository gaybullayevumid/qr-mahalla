from django.contrib import admin
from .models import Region, District, Mahalla


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "region")
    list_filter = ("region",)


@admin.register(Mahalla)
class MahallaAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "district", "get_admin")
    list_filter = ("district",)
    ordering = ("id",)  # Add explicit ordering
    list_per_page = 50  # Add pagination
    show_full_result_count = False  # Disable full count to avoid pagination issues

    def get_admin(self, obj):
        """Display admin user safely"""
        if obj.admin:
            return str(obj.admin)
        return "-"

    get_admin.short_description = "Admin"

    def get_queryset(self, request):
        """Override queryset to ensure proper ordering"""
        qs = super().get_queryset(request)
        return qs.select_related("district", "admin").order_by("id")
