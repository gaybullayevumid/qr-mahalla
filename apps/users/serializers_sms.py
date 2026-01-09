from rest_framework import serializers
from .models_sms import SMSLog


class SMSLogSerializer(serializers.ModelSerializer):
    """SMS log uchun serializer"""

    user_phone = serializers.CharField(source="user.phone", read_only=True)
    sms_type_display = serializers.CharField(
        source="get_sms_type_display", read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = SMSLog
        fields = [
            "id",
            "phone",
            "user",
            "user_phone",
            "message",
            "sms_type",
            "sms_type_display",
            "status",
            "status_display",
            "error_message",
            "created_at",
            "sent_at",
        ]
        read_only_fields = fields


class SMSStatisticsSerializer(serializers.Serializer):
    """SMS statistikasi uchun serializer"""

    total_sms = serializers.IntegerField(read_only=True)
    sent_sms = serializers.IntegerField(read_only=True)
    failed_sms = serializers.IntegerField(read_only=True)
    pending_sms = serializers.IntegerField(read_only=True)

    verification_sms = serializers.IntegerField(read_only=True)
    registration_sms = serializers.IntegerField(read_only=True)
    qr_scan_sms = serializers.IntegerField(read_only=True)
    notification_sms = serializers.IntegerField(read_only=True)

    success_rate = serializers.FloatField(read_only=True)
