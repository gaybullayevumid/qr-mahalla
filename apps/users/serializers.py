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

    def to_representation(self, instance):
        """Convert House instance to dictionary for response"""
        from apps.houses.models import House

        if isinstance(instance, House):
            return {
                "id": instance.id,
                "mahalla": instance.mahalla.id,
                "district": instance.mahalla.district.id,
                "region": instance.mahalla.district.region.id,
                "house_number": instance.house_number or "",
                "address": instance.address,
            }
        return super().to_representation(instance)

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

                if district_id and mahalla.district.id != district_id:
                    raise serializers.ValidationError(
                        f"Mahalla {mahalla.name} does not belong to district ID {district_id}"
                    )

                if region_id and mahalla.district.region.id != region_id:
                    raise serializers.ValidationError(
                        f"Mahalla {mahalla.name} does not belong to region ID {region_id}"
                    )

            except Mahalla.DoesNotExist:
                raise serializers.ValidationError(
                    f"Mahalla with ID {mahalla_id} does not exist"
                )

        return data


class UserMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal user information serializer.

    Returns only essential user data: ID, phone, first name, and last name.
    Used for QR code scanning and basic user references.
    """

    class Meta:
        model = User
        fields = ("id", "phone", "first_name", "last_name")
        read_only_fields = ("id", "phone", "first_name", "last_name")


class UserListSerializer(serializers.ModelSerializer):
    """
    User list serializer with associated houses.

    Implements role-based field filtering to control what data
    different user roles can access.
    """

    houses = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "phone",
            "first_name",
            "last_name",
            "role",
            "is_verified",
            "houses",
        )
        read_only_fields = ("id",)

    def get_houses(self, obj):
        """
        Get all houses owned by this user with their scanned QR codes.

        Access is role-based:
        - Admin/Government/Leader: can see all houses
        - Client: can only see their own houses
        """
        from apps.houses.models import House
        from apps.qrcodes.models import QRCode

        request = self.context.get("request")

        if not request or not request.user or not request.user.is_authenticated:
            return []

        user_role = getattr(request.user, "role", "client")

        if user_role in ["admin", "gov", "leader"]:
            pass
        elif user_role == "client" and obj.id != request.user.id:
            return []

        houses = House.objects.filter(owner=obj).select_related(
            "mahalla__district__region"
        )

        house_list = []
        for house in houses:
            # Get first QR code for this house (ForeignKey allows multiple)
            qr_code = house.qr_codes.first()
            scanned_qr = qr_code.uuid if qr_code else None

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

    def to_representation(self, instance):
        """
        Filter fields based on the requesting user's role.

        - Unauthenticated: minimal data only
        - Admin/Government/Leader: all data
        - Client: full data for self, minimal for others
        """
        request = self.context.get("request")

        data = super().to_representation(instance)

        if (
            not request
            or not hasattr(request, "user")
            or not request.user.is_authenticated
        ):
            return {
                "id": data.get("id"),
                "phone": data.get("phone"),
                "first_name": data.get("first_name"),
                "last_name": data.get("last_name"),
            }

        user_role = getattr(request.user, "role", "client")

        if user_role in ["admin", "gov", "leader"]:
            return data

        if user_role == "client":
            if instance.id == request.user.id:
                return data
            else:
                return {
                    "id": data.get("id"),
                    "phone": data.get("phone"),
                    "first_name": data.get("first_name"),
                    "last_name": data.get("last_name"),
                }
        return {
            "id": data.get("id"),
            "phone": data.get("phone"),
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
        }


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

    def validate(self, data):
        """Validate the entire data structure."""
        return data

    def validate_phone(self, value):
        """Validate phone number format (must match Uzbekistan format)."""
        if value:
            phone_pattern = re.compile(r"^\+?998[0-9]{9}$")
            if not phone_pattern.match(value):
                raise serializers.ValidationError(
                    "Invalid phone number format. Format: +998901234567"
                )
        return value

    def create(self, validated_data):
        """
        Create a new user with associated houses.

        Sets default role to 'client' if not specified.
        Requires phone number for user creation.
        """
        from apps.houses.models import House
        from apps.regions.models import Mahalla

        houses_data = validated_data.pop("houses", [])

        if "role" not in validated_data:
            validated_data["role"] = "client"

        if "phone" not in validated_data:
            raise serializers.ValidationError(
                {"phone": "Phone number is required when creating a user"}
            )

        user = User.objects.create(**validated_data)

        for house_data in houses_data:
            mahalla_id = house_data.pop("mahalla")
            house_data.pop("region", None)
            house_data.pop("district", None)

            try:
                mahalla = Mahalla.objects.get(id=mahalla_id)
                House.objects.create(owner=user, mahalla=mahalla, **house_data)
            except Mahalla.DoesNotExist:
                pass

        return user

    def update(self, instance, validated_data):
        """
        Update user instance and their associated houses.

        Updates or creates houses as needed and removes any houses
        not included in the update data.
        """
        from apps.houses.models import House
        from apps.regions.models import Mahalla

        houses_data = validated_data.pop("houses", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if houses_data is not None:
            existing_house_ids = set(
                House.objects.filter(owner=instance).values_list("id", flat=True)
            )
            updated_house_ids = set()

            for house_data in houses_data:
                house_id = house_data.get("id")
                mahalla_id = house_data.pop("mahalla")

                try:
                    mahalla = Mahalla.objects.get(id=mahalla_id)

                    house_data.pop("region", None)
                    house_data.pop("district", None)

                    if house_id and house_id in existing_house_ids:
                        house = House.objects.get(id=house_id, owner=instance)
                        house.mahalla = mahalla
                        house.address = house_data.get("address", house.address)
                        house.house_number = house_data.get(
                            "house_number", house.house_number
                        )
                        house.save()
                        updated_house_ids.add(house_id)
                    else:
                        house = House.objects.create(
                            owner=instance,
                            mahalla=mahalla,
                            address=house_data.get("address"),
                            house_number=house_data.get("house_number", ""),
                        )
                        updated_house_ids.add(house.id)
                except Mahalla.DoesNotExist:
                    pass

            houses_to_delete = existing_house_ids - updated_house_ids
            if houses_to_delete:
                House.objects.filter(id__in=houses_to_delete, owner=instance).delete()

        return instance


class AuthSerializer(serializers.Serializer):
    """
    Combined serializer for authentication flow.

    Handles both SMS code sending and verification:
    - Without code: sends SMS verification code
    - With code: verifies code and authenticates user
    """

    phone = serializers.CharField(max_length=15)
    code = serializers.CharField(
        max_length=6, required=False, allow_blank=True, allow_null=True
    )
    device_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    device_name = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )

    def validate_phone(self, value):
        """Validate phone number format (Uzbekistan format: +998XXXXXXXXX)."""
        phone_pattern = re.compile(r"^\+?998[0-9]{9}$")
        if not phone_pattern.match(value):
            raise serializers.ValidationError(
                "Invalid phone number format. Format: +998901234567"
            )
        return value

    def validate_code(self, value):
        """Validate verification code format (must be 6 digits if provided)."""
        if value and value.strip():
            if not value.isdigit():
                raise serializers.ValidationError("Code must contain only digits")
            if len(value) != 6:
                raise serializers.ValidationError("Code must be exactly 6 digits")
        return value
