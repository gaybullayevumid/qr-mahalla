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
    house_address = serializers.CharField(source="house.address", read_only=True)
    mahalla_name = serializers.CharField(source="house.mahalla.name", read_only=True)
    owner_name = serializers.SerializerMethodField()

    class Meta:
        model = QRCode
        fields = [
            "id",
            "house",
            "house_address",
            "mahalla_name",
            "owner_name",
            "image",
            "created_at",
        ]
        read_only_fields = ["id", "image", "created_at"]

    def get_owner_name(self, obj):
        if obj.house and obj.house.owner:
            return f"{obj.house.owner.first_name} {obj.house.owner.last_name}"
        return None


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
