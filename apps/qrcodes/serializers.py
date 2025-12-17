from rest_framework import serializers
from apps.houses.models import House


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
