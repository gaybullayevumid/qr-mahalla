from rest_framework import serializers
import re


class AuthSerializer(serializers.Serializer):
    """Combined serializer for both registration and verification"""

    phone = serializers.CharField(max_length=15)
    code = serializers.CharField(
        max_length=6, required=False, allow_blank=True, allow_null=True
    )
    device_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    device_name = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )

    def validate_phone(self, value):
        # Check phone number format
        phone_pattern = re.compile(r"^\+?998[0-9]{9}$")
        if not phone_pattern.match(value):
            raise serializers.ValidationError(
                "Invalid phone number format. Format: +998901234567"
            )
        return value

    def validate_code(self, value):
        # Code must contain only digits and be 6 digits (if provided)
        if value and value.strip():
            if not value.isdigit():
                raise serializers.ValidationError("Code must contain only digits")
            if len(value) != 6:
                raise serializers.ValidationError("Code must be exactly 6 digits")
        return value
