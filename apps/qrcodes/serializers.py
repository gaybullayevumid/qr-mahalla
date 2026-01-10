from typing import Optional

from rest_framework import serializers

from apps.qrcodes.models import QRCode


class BulkQRCodeGenerateSerializer(serializers.Serializer):
    """
    Serializer for bulk QR code generation.

    Validates the count of QR codes to generate.
    """

    count = serializers.IntegerField(
        min_value=1,
        max_value=1000,
        required=True,
        help_text="Number of QR codes to generate (1-1000)",
    )

    def validate_count(self, value):
        """Validate count is within acceptable range."""
        if value < 1:
            raise serializers.ValidationError(
                "Kamida 1 ta QR kod yaratish kerak. / At least 1 QR code must be generated."
            )
        if value > 1000:
            raise serializers.ValidationError(
                "Bir vaqtning o'zida maksimal 1000 ta QR kod yaratish mumkin. / Maximum 1000 QR codes can be generated at once."
            )
        return value


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
    mahalla = serializers.IntegerField()


class AgentCreateUserSerializer(serializers.Serializer):
    """
    Serializer for agent to create a new user and claim house.

    Used when agent scans QR code and wants to register a new user with their house.
    Agent fills in user data on behalf of the user.
    """

    phone = serializers.CharField(max_length=15, required=True)
    first_name = serializers.CharField(max_length=100, required=True)
    last_name = serializers.CharField(max_length=100, required=True)
    address = serializers.CharField(max_length=255, required=True)
    house_number = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")
    mahalla = serializers.IntegerField(required=True)

    def validate_phone(self, value):
        """Validate phone number format and uniqueness."""
        import re
        from apps.users.models import User

        # Remove all non-digit characters
        phone = re.sub(r'\D', '', value)
        
        # Check if phone number already exists
        if User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError(
                "Bu telefon raqami allaqachon ro'yxatdan o'tgan. / This phone number is already registered."
            )
        
        return phone
