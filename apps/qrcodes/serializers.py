from rest_framework import serializers
from apps.qrcodes.models import QRCode


class QRCodeSerializer(serializers.ModelSerializer):
    """QR code serializer with basic information"""

    is_claimed = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    qr_url = serializers.SerializerMethodField()

    class Meta:
        model = QRCode
        fields = ["id", "uuid", "qr_url", "image", "is_claimed", "owner", "created_at"]
        read_only_fields = ["id", "uuid", "qr_url", "image", "created_at"]

    def get_is_claimed(self, obj):
        return obj.house.owner is not None

    def get_owner(self, obj):
        """Return owner ID if house is claimed"""
        if obj.house.owner:
            return obj.house.owner.id
        return None

    def get_qr_url(self, obj):
        """Return Telegram bot URL for QR code"""
        return obj.get_qr_url()


class QRCodeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating QR codes"""

    class Meta:
        model = QRCode
        fields = ["house"]

    def validate_house(self, value):
        if QRCode.objects.filter(house=value).exists():
            raise serializers.ValidationError("QR code already exists for this house")
        return value


class QRCodeClaimSerializer(serializers.Serializer):
    """Serializer for claiming house ownership"""

    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
