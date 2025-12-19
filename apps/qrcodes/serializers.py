from rest_framework import serializers
from apps.houses.models import House
from apps.qrcodes.models import QRCode


class PublicHouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = House
        fields = ("address",)


class OwnerPublicSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField()


class OwnerPrivateSerializer(OwnerPublicSerializer):
    passport_id = serializers.CharField()
    address = serializers.CharField()


class QRCodeSerializer(serializers.ModelSerializer):
    is_claimed = serializers.SerializerMethodField()

    class Meta:
        model = QRCode
        fields = [
            "id",
            "uuid",
            "image",
            "is_delivered",
            "is_claimed",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "uuid",
            "image",
            "created_at",
            "is_delivered",
        ]

    def get_is_claimed(self, obj):
        """Check if house has an owner"""
        return obj.house.owner is not None


class QRCodeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCode
        fields = ["house"]

    def validate_house(self, value):
        # Check if QR code already exists for this house
        if QRCode.objects.filter(house=value).exists():
            raise serializers.ValidationError("QR code already exists for this house")
        return value


class QRCodeClaimSerializer(serializers.Serializer):
    """Serializer for claiming house ownership via QR code"""

    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    passport_id = serializers.CharField(max_length=20)
    address = serializers.CharField(max_length=255)


class QRCodeDeliverySerializer(serializers.Serializer):
    """Serializer for marking QR code as delivered"""

    qr_id = serializers.CharField(max_length=16)
