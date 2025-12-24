from rest_framework import serializers
import re
from .models import User


class HouseNestedSerializer(serializers.Serializer):
    """Nested serializer for houses in user data"""

    id = serializers.IntegerField(required=False, allow_null=True)
    region = serializers.IntegerField(required=False, allow_null=True)
    district = serializers.IntegerField(required=False, allow_null=True)
    mahalla = serializers.IntegerField(required=True)
    house_number = serializers.CharField(
        max_length=50, required=False, allow_blank=True, default=""
    )
    address = serializers.CharField(max_length=255, required=True)

    def validate(self, data):
        """Validate that mahalla belongs to district and region if provided"""
        from apps.regions.models import Mahalla, District, Region

        mahalla_id = data.get("mahalla")
        district_id = data.get("district")
        region_id = data.get("region")

        if mahalla_id:
            try:
                mahalla = Mahalla.objects.select_related("district__region").get(
                    id=mahalla_id
                )

                # Validate district matches
                if district_id and mahalla.district.id != district_id:
                    raise serializers.ValidationError(
                        f"Mahalla {mahalla.name} does not belong to district ID {district_id}"
                    )

                # Validate region matches
                if region_id and mahalla.district.region.id != region_id:
                    raise serializers.ValidationError(
                        f"Mahalla {mahalla.name} does not belong to region ID {region_id}"
                    )

            except Mahalla.DoesNotExist:
                raise serializers.ValidationError(
                    f"Mahalla with ID {mahalla_id} does not exist"
                )

        return data


class UserListSerializer(serializers.ModelSerializer):
    """User list serializer with houses - supports nested house CRUD"""

    houses = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "phone",
            "first_name",
            "last_name",
            "passport_id",
            "address",
            "role",
            "is_verified",
            "houses",
        )
        read_only_fields = ("id",)

    def get_houses(self, obj):
        """Get all houses owned by this user with their scanned QR codes"""
        from apps.houses.models import House
        from apps.qrcodes.models import QRCode

        houses = House.objects.filter(owner=obj).select_related(
            "mahalla__district__region"
        )

        house_list = []
        for house in houses:
            # Get QR code for this house
            try:
                qr_code = QRCode.objects.get(house=house)
                scanned_qr = qr_code.uuid
            except QRCode.DoesNotExist:
                scanned_qr = None

            house_list.append(
                {
                    "id": house.id,
                    "address": house.address,
                    "house_number": house.house_number,
                    "mahalla": house.mahalla.name,
                    "district": house.mahalla.district.name,
                    "region": house.mahalla.district.region.name,
                    "scanned_qr_code": scanned_qr,
                }
            )

        return house_list


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating users with nested houses"""

    houses = HouseNestedSerializer(many=True, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "phone",
            "first_name",
            "last_name",
            "passport_id",
            "address",
            "role",
            "houses",
        )
        read_only_fields = ("id",)
        extra_kwargs = {
            "phone": {"required": False},  # Make phone optional for updates
            "first_name": {"required": False},
            "last_name": {"required": False},
            "role": {"required": False},
        }

    def validate_phone(self, value):
        """Validate phone number format"""
        if value:
            phone_pattern = re.compile(r"^\+?998[0-9]{9}$")
            if not phone_pattern.match(value):
                raise serializers.ValidationError(
                    "Invalid phone number format. Format: +998901234567"
                )
        return value

    def create(self, validated_data):
        """Create user with houses"""
        from apps.houses.models import House
        from apps.regions.models import Mahalla

        houses_data = validated_data.pop("houses", [])

        # Set default role if not provided
        if "role" not in validated_data:
            validated_data["role"] = "user"

        # Ensure phone is provided for user creation
        if "phone" not in validated_data:
            raise serializers.ValidationError(
                {"phone": "Phone number is required when creating a user"}
            )

        user = User.objects.create(**validated_data)

        # Create houses for this user
        for house_data in houses_data:
            mahalla_id = house_data.pop("mahalla")
            # Remove region and district as they're not part of House model
            house_data.pop("region", None)
            house_data.pop("district", None)

            try:
                mahalla = Mahalla.objects.get(id=mahalla_id)
                House.objects.create(owner=user, mahalla=mahalla, **house_data)
            except Mahalla.DoesNotExist:
                pass  # Skip if mahalla not found

        return user

    def update(self, instance, validated_data):
        """Update user and their houses"""
        from apps.houses.models import House
        from apps.regions.models import Mahalla

        houses_data = validated_data.pop("houses", None)

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update houses if provided
        if houses_data is not None:
            # Get existing house IDs
            existing_house_ids = set(
                House.objects.filter(owner=instance).values_list("id", flat=True)
            )
            updated_house_ids = set()

            for house_data in houses_data:
                house_id = house_data.get("id")
                mahalla_id = house_data.pop("mahalla")

                try:
                    mahalla = Mahalla.objects.get(id=mahalla_id)

                    # Remove region and district as they're not part of House model
                    house_data.pop("region", None)
                    house_data.pop("district", None)

                    if house_id and house_id in existing_house_ids:
                        # Update existing house
                        house = House.objects.get(id=house_id, owner=instance)
                        house.mahalla = mahalla
                        house.address = house_data.get("address", house.address)
                        house.house_number = house_data.get(
                            "house_number", house.house_number
                        )
                        house.save()
                        updated_house_ids.add(house_id)
                    else:
                        # Create new house
                        house = House.objects.create(
                            owner=instance,
                            mahalla=mahalla,
                            address=house_data.get("address"),
                            house_number=house_data.get("house_number", ""),
                        )
                        updated_house_ids.add(house.id)
                except Mahalla.DoesNotExist:
                    pass  # Skip if mahalla not found

            # Delete houses that were not in the update
            houses_to_delete = existing_house_ids - updated_house_ids
            if houses_to_delete:
                House.objects.filter(id__in=houses_to_delete, owner=instance).delete()

        return instance


class AuthSerializer(serializers.Serializer):
    """Combined serializer for both registration and verification"""

    phone = serializers.CharField(max_length=15)
    code = serializers.CharField(
        max_length=6, required=False, allow_blank=True, allow_null=True
    )
    device_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    device_name = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )

    def validate_phone(self, value):
        # Check phone number format
        phone_pattern = re.compile(r"^\+?998[0-9]{9}$")
        if not phone_pattern.match(value):
            raise serializers.ValidationError(
                "Invalid phone number format. Format: +998901234567"
            )
        return value

    def validate_code(self, value):
        # Code must contain only digits and be 6 digits (if provided)
        if value and value.strip():
            if not value.isdigit():
                raise serializers.ValidationError("Code must contain only digits")
            if len(value) != 6:
                raise serializers.ValidationError("Code must be exactly 6 digits")
        return value
