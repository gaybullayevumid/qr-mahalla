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
    """Create house"""

    class Meta:
        model = House
        fields = ("mahalla", "house_number", "address", "owner")
        extra_kwargs = {"owner": {"required": False}}

    def validate_mahalla(self, value):
        # value could be either Mahalla instance or integer ID
        mahalla_id = value.id if hasattr(value, "id") else value
        if not Mahalla.objects.filter(id=mahalla_id).exists():
            raise serializers.ValidationError("Mahalla not found")
        return value

    def validate_owner(self, value):
        if value:
            # value could be either User instance or integer ID
            owner_id = value.id if hasattr(value, "id") else value
            if not User.objects.filter(id=owner_id).exists():
                raise serializers.ValidationError("Owner not found")
        return value
