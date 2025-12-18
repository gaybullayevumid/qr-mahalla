from rest_framework import serializers
import re


class RegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

    def validate_phone(self, value):
        # Telefon raqam formatini tekshirish
        phone_pattern = re.compile(r"^\+?998[0-9]{9}$")
        if not phone_pattern.match(value):
            raise serializers.ValidationError(
                "Telefon raqam formati noto'g'ri. Format: +998901234567"
            )
        return value


class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6, min_length=6)

    def validate_code(self, value):
        # Kod faqat raqamlardan iborat bo'lishi kerak
        if not value.isdigit():
            raise serializers.ValidationError(
                "Kod faqat raqamlardan iborat bo'lishi kerak"
            )
        return value
