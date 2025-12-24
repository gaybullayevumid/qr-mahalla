from rest_framework import serializers
from .models import Region, District, Mahalla
from apps.users.models import User
from apps.houses.models import House


class MahallaNestedWriteSerializer(serializers.ModelSerializer):
    """Mahalla for write operations (nested in District)"""

    class Meta:
        model = Mahalla
        fields = ("id", "name", "admin")
        extra_kwargs = {"id": {"required": False}}


class MahallaSerializer(serializers.ModelSerializer):
    """Neighborhood serializer - with district ID"""

    class Meta:
        model = Mahalla
        fields = ("id", "name", "district", "admin")
        read_only_fields = ("id",)


class MahallaCreateSerializer(serializers.ModelSerializer):
    """Create neighborhood"""

    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all())
    admin = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Mahalla
        fields = ("name", "district", "admin")


class MahallaNestedSerializer(serializers.ModelSerializer):
    """Neighborhood nested serializer - inside district"""

    admin_name = serializers.SerializerMethodField()
    users = serializers.SerializerMethodField()

    class Meta:
        model = Mahalla
        fields = ("id", "name", "admin", "admin_name", "users")

    def get_admin_name(self, obj):
        if obj.admin:
            return f"{obj.admin.first_name} {obj.admin.last_name}"
        return None

    def get_users(self, obj):
        """Get all user IDs (house owners) in this mahalla"""
        houses = House.objects.filter(mahalla=obj, owner__isnull=False).select_related(
            "owner"
        )
        user_ids = list(set(house.owner.id for house in houses))
        return user_ids


class DistrictSerializer(serializers.ModelSerializer):
    """District serializer - with region ID"""

    class Meta:
        model = District
        fields = ("id", "name", "region")
        read_only_fields = ("id",)


class DistrictCreateSerializer(serializers.ModelSerializer):
    """Create district"""

    region = serializers.PrimaryKeyRelatedField(queryset=Region.objects.all())

    class Meta:
        model = District
        fields = ("name", "region")


class DistrictNestedSerializer(serializers.ModelSerializer):
    """District nested serializer - inside region with neighborhoods"""

    neighborhoods = MahallaNestedSerializer(
        many=True, read_only=True, source="mahallas"
    )

    class Meta:
        model = District
        fields = ("id", "name", "neighborhoods")


class DistrictNestedWriteSerializer(serializers.ModelSerializer):
    """District for write operations (nested in Region or standalone)"""

    mahallas = MahallaNestedWriteSerializer(many=True, required=False)
    region = serializers.PrimaryKeyRelatedField(
        queryset=Region.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = District
        fields = ("id", "name", "region", "mahallas")
        extra_kwargs = {
            "id": {"required": False},
        }

    def create(self, validated_data):
        """Create district with nested mahallas"""
        mahallas_data = validated_data.pop("mahallas", [])

        # Ensure region is provided for standalone district creation
        if "region" not in validated_data or validated_data["region"] is None:
            raise serializers.ValidationError(
                {"region": "Region is required when creating a district"}
            )

        district = District.objects.create(**validated_data)

        for mahalla_data in mahallas_data:
            Mahalla.objects.create(district=district, **mahalla_data)

        return district

    def update(self, instance, validated_data):
        """Update district and nested mahallas"""
        mahallas_data = validated_data.pop("mahallas", None)

        # Update district fields
        instance.name = validated_data.get("name", instance.name)
        if "region" in validated_data:
            instance.region = validated_data.get("region")
        instance.save()

        # Update mahallas if provided
        if mahallas_data is not None:
            existing_mahalla_ids = []
            for mahalla_data in mahallas_data:
                mahalla_id = mahalla_data.get("id")

                if mahalla_id:
                    # Update existing mahalla
                    try:
                        mahalla = Mahalla.objects.get(id=mahalla_id, district=instance)
                        mahalla.name = mahalla_data.get("name", mahalla.name)
                        mahalla.admin = mahalla_data.get("admin", mahalla.admin)
                        mahalla.save()
                        existing_mahalla_ids.append(mahalla.id)
                    except Mahalla.DoesNotExist:
                        pass
                else:
                    # Create new mahalla
                    mahalla = Mahalla.objects.create(district=instance, **mahalla_data)
                    existing_mahalla_ids.append(mahalla.id)

            # Delete mahallas not in the update
            instance.mahallas.exclude(id__in=existing_mahalla_ids).delete()

        return instance


class RegionSerializer(serializers.ModelSerializer):
    """Region serializer - simple"""

    class Meta:
        model = Region
        fields = ("id", "name")
        read_only_fields = ("id",)


class RegionWriteSerializer(serializers.ModelSerializer):
    """Region write serializer - with nested districts and mahallas"""

    districts = DistrictNestedWriteSerializer(many=True, required=False)

    class Meta:
        model = Region
        fields = ("id", "name", "districts")
        read_only_fields = ("id",)

    def create(self, validated_data):
        districts_data = validated_data.pop("districts", [])
        region = Region.objects.create(**validated_data)

        for district_data in districts_data:
            mahallas_data = district_data.pop("mahallas", [])
            district = District.objects.create(region=region, **district_data)

            for mahalla_data in mahallas_data:
                Mahalla.objects.create(district=district, **mahalla_data)

        return region

    def update(self, instance, validated_data):
        districts_data = validated_data.pop("districts", None)
        instance.name = validated_data.get("name", instance.name)
        instance.save()

        if districts_data is not None:
            # Update or create districts
            existing_district_ids = []
            for district_data in districts_data:
                mahallas_data = district_data.pop("mahallas", [])
                district_id = district_data.get("id")

                if district_id:
                    # Update existing district
                    district = District.objects.get(id=district_id, region=instance)
                    district.name = district_data.get("name", district.name)
                    district.save()
                    existing_district_ids.append(district.id)
                else:
                    # Create new district
                    district = District.objects.create(region=instance, **district_data)
                    existing_district_ids.append(district.id)

                # Handle mahallas
                if mahallas_data:
                    existing_mahalla_ids = []
                    for mahalla_data in mahallas_data:
                        mahalla_id = mahalla_data.get("id")

                        if mahalla_id:
                            # Update existing mahalla
                            mahalla = Mahalla.objects.get(
                                id=mahalla_id, district=district
                            )
                            mahalla.name = mahalla_data.get("name", mahalla.name)
                            mahalla.admin = mahalla_data.get("admin", mahalla.admin)
                            mahalla.save()
                            existing_mahalla_ids.append(mahalla.id)
                        else:
                            # Create new mahalla
                            mahalla = Mahalla.objects.create(
                                district=district, **mahalla_data
                            )
                            existing_mahalla_ids.append(mahalla.id)

                    # Delete mahallas not in the update
                    district.mahallas.exclude(id__in=existing_mahalla_ids).delete()

            # Delete districts not in the update
            instance.districts.exclude(id__in=existing_district_ids).delete()

        return instance


class RegionCreateSerializer(serializers.ModelSerializer):
    """Create region - only name required"""

    class Meta:
        model = Region
        fields = ("name",)


class RegionDetailSerializer(serializers.ModelSerializer):
    """Region detail serializer - with districts and neighborhoods"""

    districts = DistrictNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Region
        fields = ("id", "name", "districts")
