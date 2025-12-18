from rest_framework import serializers
from .models import Region, District, Mahalla


class MahallaSerializer(serializers.ModelSerializer):
    """Mahalla serializer - district ID bilan"""

    class Meta:
        model = Mahalla
        fields = ("id", "name", "district", "admin")


class MahallaCreateSerializer(serializers.ModelSerializer):
    """Mahalla yaratish uchun"""

    class Meta:
        model = Mahalla
        fields = ("name", "district", "admin")
        extra_kwargs = {"admin": {"required": False}}

    def validate_district(self, value):
        if not District.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Tuman topilmadi")
        return value


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


class DistrictCreateSerializer(serializers.ModelSerializer):
    """District yaratish uchun"""

    class Meta:
        model = District
        fields = ("name", "region")

    def validate_region(self, value):
        if not Region.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Region topilmadi")
        return value


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
