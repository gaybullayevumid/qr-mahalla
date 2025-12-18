from rest_framework import serializers
from .models import Region, District, Mahalla


class MahallaSerializer(serializers.ModelSerializer):
    """Neighborhood serializer - with district ID"""

    class Meta:
        model = Mahalla
        fields = ("id", "name", "district", "admin")


class MahallaCreateSerializer(serializers.ModelSerializer):
    """Create neighborhood"""

    class Meta:
        model = Mahalla
        fields = ("name", "district", "admin")
        extra_kwargs = {"admin": {"required": False}}

    def validate_district(self, value):
        if not District.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("District not found")
        return value


class MahallaNestedSerializer(serializers.ModelSerializer):
    """Neighborhood nested serializer - inside district"""

    admin_name = serializers.SerializerMethodField()

    class Meta:
        model = Mahalla
        fields = ("id", "name", "admin", "admin_name")

    def get_admin_name(self, obj):
        if obj.admin:
            return f"{obj.admin.first_name} {obj.admin.last_name}"
        return None


class DistrictSerializer(serializers.ModelSerializer):
    """District serializer - with region ID"""

    class Meta:
        model = District
        fields = ("id", "name", "region")


class DistrictCreateSerializer(serializers.ModelSerializer):
    """Create district"""

    class Meta:
        model = District
        fields = ("name", "region")

    def validate_region(self, value):
        if not Region.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Region not found")
        return value


class DistrictNestedSerializer(serializers.ModelSerializer):
    """District nested serializer - inside region with neighborhoods"""

    mahallas = MahallaNestedSerializer(many=True, read_only=True)

    class Meta:
        model = District
        fields = ("id", "name", "mahallas")


class RegionSerializer(serializers.ModelSerializer):
    """Region serializer - simple"""

    class Meta:
        model = Region
        fields = ("id", "name")


class RegionDetailSerializer(serializers.ModelSerializer):
    """Region detail serializer - with districts and neighborhoods"""

    districts = DistrictNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Region
        fields = ("id", "name", "districts")
