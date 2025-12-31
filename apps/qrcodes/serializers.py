from typing import Optional

from rest_framework import serializers

from apps.qrcodes.models import QRCode


class QRCodeSerializer(serializers.ModelSerializer):
    """
    QR code serializer with basic information.

    Includes computed fields for claim status, owner, and QR URL.
    """

    is_claimed = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    qr_url = serializers.SerializerMethodField()

    class Meta:
        model = QRCode
        fields = ["id", "uuid", "qr_url", "image", "is_claimed", "owner", "created_at"]
        read_only_fields = ["id", "uuid", "qr_url", "image", "created_at"]

    def get_is_claimed(self, obj: QRCode) -> bool:
        """Check if QR code is claimed (has house with owner)."""
        return bool(obj.house and obj.house.owner is not None)

    def get_owner(self, obj: QRCode) -> Optional[int]:
        """Return owner ID if house is claimed, None otherwise."""
        if obj.house and obj.house.owner:
            return obj.house.owner.id
        return None

    def get_qr_url(self, obj: QRCode) -> str:
        """Return Telegram bot URL for QR code."""
        return obj.get_qr_url()


class QRCodeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating QR codes.

    Validates that house doesn't already have a QR code.
    """

    class Meta:
        model = QRCode
        fields = ["house"]

    def validate_house(self, value):
        """Ensure house doesn't already have a QR code."""
        if QRCode.objects.filter(house=value).exists():
            raise serializers.ValidationError("QR code already exists for this house")
        return value


class QRCodeClaimSerializer(serializers.Serializer):
    """
    Serializer for claiming house ownership.

    Used when user scans unclaimed QR code and wants to claim the house.
    """

    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    address = serializers.CharField(max_length=255)
    house_number = serializers.CharField(max_length=50)
    mahalla = serializers.IntegerField()  # Mahalla ID
