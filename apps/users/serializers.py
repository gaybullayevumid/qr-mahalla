from rest_framework import serializers
import re


class RegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

    def validate_phone(self, value):
        # Check phone number format
        phone_pattern = re.compile(r"^\+?998[0-9]{9}$")
        if not phone_pattern.match(value):
            raise serializers.ValidationError(
                "Invalid phone number format. Format: +998901234567"
            )
        return value


class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6, min_length=6)

    def validate_code(self, value):
        # Code must contain only digits
        if not value.isdigit():
            raise serializers.ValidationError("Code must contain only digits")
        return value
