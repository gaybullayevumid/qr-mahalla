from rest_framework import serializers
from .models import Region, District, Mahalla
from apps.users.models import User
from apps.houses.models import House


class MahallaNestedWriteSerializer(serializers.ModelSerializer):
    """
    Mahalla serializer for write operations when nested in District.

    Supports creating and updating mahallas within a district context.
    """

    class Meta:
        model = Mahalla
        fields = ("id", "name", "admin")
        extra_kwargs = {"id": {"required": False, "read_only": False}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "id" in self.fields:
            self.fields["id"].validators = []


class MahallaSerializer(serializers.ModelSerializer):
    """
    Neighborhood serializer with district ID.

    Provides basic neighborhood information including its district.
    """

    class Meta:
        model = Mahalla
        fields = ("id", "name", "district", "admin")
        read_only_fields = ("id",)


class MahallaCreateSerializer(serializers.ModelSerializer):
    """
    Neighborhood serializer for creation.

    Handles the creation of new neighborhoods with district assignment.
    """

    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all())
    admin = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Mahalla
        fields = ("name", "district", "admin")


class MahallaNestedSerializer(serializers.ModelSerializer):
    """
    Neighborhood serializer for nested representation within a district.

    Includes admin information and list of user IDs.
    """

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
        """
        Get all user IDs of house owners in this mahalla.

        Args:
            obj: The Mahalla instance.

        Returns:
            list: List of unique user IDs.
        """
        houses = House.objects.filter(mahalla=obj, owner__isnull=False).select_related(
            "owner"
        )
        user_ids = list(set(house.owner.id for house in houses))
        return user_ids


class DistrictSerializer(serializers.ModelSerializer):
    """
    District serializer with region ID.

    Provides basic district information including its region.
    """

    class Meta:
        model = District
        fields = ("id", "name", "region")
        read_only_fields = ("id",)


class DistrictCreateSerializer(serializers.ModelSerializer):
    """
    District serializer for creation.

    Handles the creation of new districts with region assignment.
    """

    region = serializers.PrimaryKeyRelatedField(queryset=Region.objects.all())

    class Meta:
        model = District
        fields = ("name", "region")


class DistrictNestedSerializer(serializers.ModelSerializer):
    """
    District serializer for nested representation within a region.

    Includes nested neighborhoods (mahallas) information.
    """

    neighborhoods = MahallaNestedSerializer(
        many=True, read_only=True, source="mahallas"
    )

    class Meta:
        model = District
        fields = ("id", "name", "neighborhoods")


class DistrictNestedWriteSerializer(serializers.ModelSerializer):
    """
    District serializer for write operations.

    Supports creating and updating districts with nested mahallas,
    either within a region context or as standalone operations.
    """

    mahallas = MahallaNestedWriteSerializer(many=True, required=False)
    region = serializers.PrimaryKeyRelatedField(
        queryset=Region.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = District
        fields = ("id", "name", "region", "mahallas")
        extra_kwargs = {
            "id": {"required": False, "read_only": False},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "id" in self.fields:
            self.fields["id"].validators = []

    def create(self, validated_data):
        """
        Create a district with nested mahallas.

        Args:
            validated_data: Validated data containing district and mahalla information.

        Returns:
            District: The created district instance.

        Raises:
            ValidationError: If region is not provided.
        """
        mahallas_data = validated_data.pop("mahallas", [])
        if "region" not in validated_data or validated_data["region"] is None:
            raise serializers.ValidationError(
                {"region": "Region is required when creating a district"}
            )

        district = District.objects.create(**validated_data)

        for mahalla_data in mahallas_data:
            Mahalla.objects.create(district=district, **mahalla_data)

        return district

    def update(self, instance, validated_data):
        """
        Update a district and its nested mahallas.

        Args:
            instance: The district instance to update.
            validated_data: Validated data containing updates.

        Returns:
            District: The updated district instance.
        """
        mahallas_data = validated_data.pop("mahallas", None)
        instance.name = validated_data.get("name", instance.name)
        if "region" in validated_data:
            instance.region = validated_data.get("region")
        instance.save()

        if mahallas_data is not None:
            existing_mahalla_ids = []
            for mahalla_data in mahallas_data:
                mahalla_id = mahalla_data.pop("id", None)

                if mahalla_id:
                    try:
                        mahalla = Mahalla.objects.get(id=mahalla_id, district=instance)
                        mahalla.name = mahalla_data.get("name", mahalla.name)
                        mahalla.admin = mahalla_data.get("admin", mahalla.admin)
                        mahalla.save()
                        existing_mahalla_ids.append(mahalla.id)
                    except Mahalla.DoesNotExist:
                        pass
                else:
                    mahalla = Mahalla.objects.create(district=instance, **mahalla_data)
                    existing_mahalla_ids.append(mahalla.id)

            instance.mahallas.exclude(id__in=existing_mahalla_ids).delete()

        return instance


class RegionSerializer(serializers.ModelSerializer):
    """
    Simple region serializer.

    Provides basic region information.
    """

    class Meta:
        model = Region
        fields = ("id", "name")
        read_only_fields = ("id",)


class RegionWriteSerializer(serializers.ModelSerializer):
    """
    Region serializer for write operations.

    Supports creating and updating regions with nested districts and mahallas.
    """

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
            existing_district_ids = []
            for district_data in districts_data:
                mahallas_data = district_data.pop("mahallas", [])
                district_id = district_data.pop("id", None)

                if district_id:
                    district = District.objects.get(id=district_id, region=instance)
                    district.name = district_data.get("name", district.name)
                    district.save()
                    existing_district_ids.append(district.id)
                else:
                    district = District.objects.create(region=instance, **district_data)
                    existing_district_ids.append(district.id)

                if mahallas_data:
                    existing_mahalla_ids = []
                    for mahalla_data in mahallas_data:
                        mahalla_id = mahalla_data.pop("id", None)

                        if mahalla_id:
                            mahalla = Mahalla.objects.get(
                                id=mahalla_id, district=district
                            )
                            mahalla.name = mahalla_data.get("name", mahalla.name)
                            mahalla.admin = mahalla_data.get("admin", mahalla.admin)
                            mahalla.save()
                            existing_mahalla_ids.append(mahalla.id)
                        else:

                            mahalla = Mahalla.objects.create(
                                district=district, **mahalla_data
                            )
                            existing_mahalla_ids.append(mahalla.id)

                    district.mahallas.exclude(id__in=existing_mahalla_ids).delete()

            instance.districts.exclude(id__in=existing_district_ids).delete()

        return instance


class RegionCreateSerializer(serializers.ModelSerializer):
    """
    Region serializer for creation.

    Only requires the region name for creation.
    """

    class Meta:
        model = Region
        fields = ("name",)


class RegionDetailSerializer(serializers.ModelSerializer):
    """
    Region serializer for detailed representation.

    Includes nested districts and neighborhoods information.
    """

    districts = DistrictNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Region
        fields = ("id", "name", "districts")
