from rest_framework import serializers
from .models import QRCode

class PublicQRSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.get_full_name')
    phone = serializers.CharField(source='owner.phone')

    class Meta:
        model = QRCode
        fields = ('owner_name', 'phone')


class GovernmentQRSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()

    class Meta:
        model = QRCode
        fields = ('owner', 'object_type', 'created_at')

    def get_owner(self, obj):
        user = obj.owner
        return {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "father_name": user.father_name,
            "phone": user.phone,
            "passport_id": user.passport_id,
            "address": user.address,
        }
