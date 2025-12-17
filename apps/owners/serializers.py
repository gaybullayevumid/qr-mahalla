from rest_framework import serializers
from .models import OwnerProfile


class OwnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OwnerProfile
        fields = (
            "id",
            "first_name",
            "last_name",
            "phone",
            "mahalla",
            "address",
        )
