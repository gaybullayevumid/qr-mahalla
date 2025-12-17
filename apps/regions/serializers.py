from rest_framework import serializers
from .models import Region, District, Mahalla


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ("id", "name")


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ("id", "name", "region")


class MahallaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mahalla
        fields = ("id", "name", "district")
