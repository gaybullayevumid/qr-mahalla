from django.contrib import admin
from .models import House


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ("id", "address", "owner", "mahalla")
    list_filter = ("mahalla",)
    search_fields = ("address",)
