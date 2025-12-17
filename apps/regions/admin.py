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
    list_display = ("id", "name", "district", "admin")
    list_filter = ("district",)
