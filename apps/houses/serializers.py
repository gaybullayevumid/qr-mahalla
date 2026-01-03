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


class HouseCreateSerializer(serializers.Serializer):
    """
    Flexible serializer for creating houses.

    Supports two formats:
    1. Simple format (client): {mahalla, house_number, address}
       - Owner is set to current user

    2. Admin format: {phone, ownerFirstName, ownerLastName, region, district, mahalla, address, houseNumber}
       - Creates/finds user by phone
       - Region and district are IDs (not names)
    """

    # Owner fields (optional - for admin)
    phone = serializers.CharField(max_length=15, required=False, allow_blank=True)
    ownerFirstName = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )
    ownerLastName = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )

    # Location fields - all IDs (frontend select)
    region = serializers.IntegerField(required=False, allow_null=True)
    district = serializers.IntegerField(required=False, allow_null=True)
    mahalla = serializers.IntegerField(required=True)

    # House fields
    address = serializers.CharField(max_length=255, required=True)
    houseNumber = serializers.CharField(
        max_length=50, required=False, allow_blank=True, default=""
    )
    house_number = serializers.CharField(
        max_length=50, required=False, allow_blank=True, default=""
    )

    def validate_phone(self, value):
        """Normalize phone number."""
        if not value:
            return value

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
        region_id = data.get("region")
        district_id = data.get("district")

        try:
            mahalla = Mahalla.objects.select_related("district__region").get(
                id=mahalla_id
            )

            # Validate region if provided
            if region_id:
                if mahalla.district.region.id != region_id:
                    raise serializers.ValidationError(
                        {
                            "region": f"Mahalla {mahalla.name} does not belong to region ID {region_id}"
                        }
                    )

            # Validate district if provided
            if district_id:
                if mahalla.district.id != district_id:
                    raise serializers.ValidationError(
                        {
                            "district": f"Mahalla {mahalla.name} does not belong to district ID {district_id}"
                        }
                    )

            data["mahalla_obj"] = mahalla

        except Mahalla.DoesNotExist:
            raise serializers.ValidationError(
                {"mahalla": f"Mahalla with ID {mahalla_id} does not exist"}
            )

        return data

    def create(self, validated_data):
        """Create house with owner."""
        mahalla = validated_data["mahalla_obj"]
        address = validated_data["address"]

        # Get house_number from either field name
        house_number = validated_data.get("houseNumber") or validated_data.get(
            "house_number", ""
        )

        phone = validated_data.get("phone")

        # If phone provided (admin format), create/find user
        if phone:
            first_name = validated_data.get("ownerFirstName", "")
            last_name = validated_data.get("ownerLastName", "")

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
        else:
            # Use current user from request context
            request = self.context.get("request")
            user = request.user if request else None

        # Create house
        house = House.objects.create(
            owner=user, mahalla=mahalla, address=address, house_number=house_number
        )

        return house

    def to_representation(self, instance):
        """Return house data with full details."""
        return {
            "id": instance.id,
            "owner": (
                {
                    "id": instance.owner.id,
                    "phone": instance.owner.phone,
                    "firstName": instance.owner.first_name,
                    "lastName": instance.owner.last_name,
                }
                if instance.owner
                else None
            ),
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
