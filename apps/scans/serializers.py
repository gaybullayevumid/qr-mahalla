from rest_framework import serializers
from .models import ScanLog


class ScanLogSerializer(serializers.ModelSerializer):
    qr = serializers.StringRelatedField()
    scanned_by = serializers.StringRelatedField()

    class Meta:
        model = ScanLog
        fields = (
            "id",
            "qr",
            "scanned_by",
            "ip_address",
            "created_at",
        )
