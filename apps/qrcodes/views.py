from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import QRCode
from .serializers import (
    PublicOwnerSerializer,
    GovernmentOwnerSerializer,
)


class QRScanView(APIView):
    """
    QR scan endpoint:
    /api/scan/<uuid>/
    """

    authentication_classes = []   # oddiy user uchun ham ochiq
    permission_classes = []

    def get(self, request, qr_id):
        qr = get_object_or_404(QRCode, id=qr_id, is_active=True)
        owner = qr.owner

        # scan log yozish
        ScanLog.objects.create(
            qr=qr,
            scanned_by=request.user if request.user.is_authenticated else None,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        # agar login qilinmagan bo‘lsa
        if not request.user.is_authenticated:
            data = PublicOwnerSerializer(owner).data
            return Response({
                "role": "guest",
                "owner": data
            })

        # owner o‘zi
        if request.user == owner:
            return Response({
                "message": "Bu QR code sizga tegishli"
            })

        # davlat xodimi
        if request.user.role == 'government':
            data = GovernmentOwnerSerializer(owner).data
            return Response({
                "role": "government",
                "owner": data
            })

        # oddiy user
        data = PublicOwnerSerializer(owner).data
        return Response({
            "role": "user",
            "owner": data
        })
