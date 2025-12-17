from rest_framework import serializers
from .models import QRCode
from apps.users.models import User


class PublicOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone")


class GovernmentOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "father_name",
            "phone",
            "address",
            "passport_id",
            "date_joined",
        )


class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCode
        fields = ("id", "created_at")
