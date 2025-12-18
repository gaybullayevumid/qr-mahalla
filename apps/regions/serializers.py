from rest_framework import serializers
from .models import Region, District, Mahalla


class MahallaSerializer(serializers.ModelSerializer):
    """Mahalla serializer - district ID bilan"""

    class Meta:
        model = Mahalla
        fields = ("id", "name", "district", "admin")


class MahallaNestedSerializer(serializers.ModelSerializer):
    """Mahalla nested serializer - district ichida"""

    admin_name = serializers.SerializerMethodField()

    class Meta:
        model = Mahalla
        fields = ("id", "name", "admin", "admin_name")

    def get_admin_name(self, obj):
        if obj.admin:
            return f"{obj.admin.first_name} {obj.admin.last_name}"
        return None


class DistrictSerializer(serializers.ModelSerializer):
    """District serializer - region ID bilan"""

    class Meta:
        model = District
        fields = ("id", "name", "region")


class DistrictNestedSerializer(serializers.ModelSerializer):
    """District nested serializer - region ichida mahallalar bilan"""

    mahallas = MahallaNestedSerializer(many=True, read_only=True)

    class Meta:
        model = District
        fields = ("id", "name", "mahallas")


class RegionSerializer(serializers.ModelSerializer):
    """Region serializer - oddiy"""

    class Meta:
        model = Region
        fields = ("id", "name")


class RegionDetailSerializer(serializers.ModelSerializer):
    """Region detail serializer - tumanlar va mahallalar bilan"""

    districts = DistrictNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Region
        fields = ("id", "name", "districts")
