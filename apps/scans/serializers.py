from rest_framework import serializers
from .models import ScanLog


class ScanLogSerializer(serializers.ModelSerializer):
    """Serializer for ScanLog with detailed information."""

    qr_id = serializers.IntegerField(source="qr.id", read_only=True)
    qr_uuid = serializers.CharField(source="qr.uuid", read_only=True)
    house_id = serializers.IntegerField(
        source="qr.house.id", read_only=True, allow_null=True
    )
    house_address = serializers.CharField(
        source="qr.house.address", read_only=True, allow_null=True
    )
    scanned_by_phone = serializers.CharField(
        source="scanned_by.phone", read_only=True, allow_null=True
    )
    scanned_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ScanLog
        fields = [
            "id",
            "qr_id",
            "qr_uuid",
            "house_id",
            "house_address",
            "scanned_by_phone",
            "scanned_by_name",
            "scanned_at",
            "ip_address",
        ]
        read_only_fields = ["id", "scanned_at"]

    def get_scanned_by_name(self, obj):
        """Get full name of user who scanned."""
        if obj.scanned_by:
            return f"{obj.scanned_by.first_name} {obj.scanned_by.last_name}".strip()
        return None
