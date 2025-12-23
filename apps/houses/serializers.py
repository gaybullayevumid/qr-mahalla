from rest_framework import serializers
from .models import House
from apps.regions.models import Mahalla
from apps.users.models import User


class HouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = House
        fields = (
            "id",
            "owner",
            "mahalla",
            "house_number",
            "address",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class HouseCreateSerializer(serializers.ModelSerializer):
    """Create house - owner is set automatically"""

    mahalla = serializers.PrimaryKeyRelatedField(
        queryset=Mahalla.objects.all(), required=True
    )

    class Meta:
        model = House
        fields = ("mahalla", "house_number", "address")

    def validate_mahalla(self, value):
        """Allow all authenticated users to use any mahalla ID"""
        return value
