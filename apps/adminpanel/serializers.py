from rest_framework import serializers
from ..users.models import User
from ..qrcodes.models import QRCode
from ..scans.models import ScanLog


class UserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "phone",
            "role",
            "is_active",
            "is_verified",
        )


class UserRoleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("role",)


class QRCodeAdminSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()

    class Meta:
        model = QRCode
        fields = (
            "id",
            "owner",
            "is_active",
            "created_at",
        )


class ScanLogAdminSerializer(serializers.ModelSerializer):
    qr = serializers.StringRelatedField()
    scanned_by = serializers.StringRelatedField()

    class Meta:
        model = ScanLog
        fields = (
            "id",
            "qr",
            "scanned_by",
            "ip_address",
            "created_at",
        )
