from rest_framework import serializers
from .models import House
from apps.regions.models import Mahalla, District, Region
from apps.users.models import User


class HouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = House
        fields = (
            "id",
            "owner",
            "mahalla",
            "house_number",
            "address",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class HouseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating houses.

    The owner field is set automatically to the current user.
    """

    mahalla = serializers.PrimaryKeyRelatedField(
        queryset=Mahalla.objects.all(), required=True
    )

    class Meta:
        model = House
        fields = ("mahalla", "house_number", "address")

    def validate_mahalla(self, value):
        """Validate mahalla field.

        All authenticated users can use any mahalla ID.
        """
        return value


class HouseAdminCreateSerializer(serializers.Serializer):
    """
    Admin serializer for creating houses with owner details.

    Accepts region/district names or mahalla ID.
    Creates or finds user by phone.
    """

    # Owner fields
    phone = serializers.CharField(max_length=15, required=True)
    ownerFirstName = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )
    ownerLastName = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )

    # Location fields (flexible - can use names or IDs)
    region = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    district = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    mahalla = serializers.IntegerField(required=True)

    # House fields
    address = serializers.CharField(max_length=255, required=True)
    houseNumber = serializers.CharField(
        max_length=50, required=False, allow_blank=True, default=""
    )

    def validate_phone(self, value):
        """Normalize phone number."""
        phone = value.strip()

        # If starts with +998, keep it
        if phone.startswith("+998"):
            return phone

        # If starts with 998, add +
        if phone.startswith("998"):
            return "+" + phone

        # Otherwise add +998
        if not phone.startswith("+"):
            return "+998" + phone

        return phone

    def validate(self, data):
        """Validate mahalla exists and belongs to region/district if provided."""
        mahalla_id = data.get("mahalla")
        region_name = data.get("region")
        district_name = data.get("district")

        try:
            mahalla = Mahalla.objects.select_related("district__region").get(
                id=mahalla_id
            )

            # Validate region if provided
            if region_name:
                if mahalla.district.region.name.lower() != region_name.lower():
                    raise serializers.ValidationError(
                        {
                            "region": f"Mahalla ID {mahalla_id} does not belong to region '{region_name}'"
                        }
                    )

            # Validate district if provided
            if district_name:
                if mahalla.district.name.lower() != district_name.lower():
                    raise serializers.ValidationError(
                        {
                            "district": f"Mahalla ID {mahalla_id} does not belong to district '{district_name}'"
                        }
                    )

            data["mahalla_obj"] = mahalla

        except Mahalla.DoesNotExist:
            raise serializers.ValidationError(
                {"mahalla": f"Mahalla with ID {mahalla_id} does not exist"}
            )

        return data

    def create(self, validated_data):
        """Create house with owner (create user if not exists)."""
        phone = validated_data["phone"]
        first_name = validated_data.get("ownerFirstName", "")
        last_name = validated_data.get("ownerLastName", "")
        mahalla = validated_data["mahalla_obj"]
        address = validated_data["address"]
        house_number = validated_data.get("houseNumber", "")

        # Get or create user
        user, created = User.objects.get_or_create(
            phone=phone,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "role": "client",
            },
        )

        # Update user name if user exists but name was provided
        if not created and (first_name or last_name):
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            user.save(update_fields=["first_name", "last_name"])

        # Create house
        house = House.objects.create(
            owner=user, mahalla=mahalla, address=address, house_number=house_number
        )

        return house

    def to_representation(self, instance):
        """Return house data with full details."""
        return {
            "id": instance.id,
            "owner": {
                "id": instance.owner.id,
                "phone": instance.owner.phone,
                "firstName": instance.owner.first_name,
                "lastName": instance.owner.last_name,
            },
            "mahalla": {
                "id": instance.mahalla.id,
                "name": instance.mahalla.name,
                "district": {
                    "id": instance.mahalla.district.id,
                    "name": instance.mahalla.district.name,
                    "region": {
                        "id": instance.mahalla.district.region.id,
                        "name": instance.mahalla.district.region.name,
                    },
                },
            },
            "address": instance.address,
            "houseNumber": instance.house_number,
            "createdAt": instance.created_at.isoformat(),
        }
