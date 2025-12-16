from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from .models import QRCode, ScanLog
from .serializers import PublicQRSerializer, GovernmentQRSerializer

class QRScanView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, qr_id):
        qr = get_object_or_404(QRCode, id=qr_id)

        ScanLog.objects.create(
            qr=qr,
            scanned_by=request.user if request.user.is_authenticated else None,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        if request.user.is_authenticated and request.user == qr.owner:
            return Response({
                "message": "Bu QR kod sizga tegishli",
                "manage_url": f"/api/qrcodes/{qr.id}/manage/"
            })

        if (
            request.user.is_authenticated and
            request.user.role == 'government' and
            request.user.is_verified
        ):
            return Response(GovernmentQRSerializer(qr).data)

        return Response(PublicQRSerializer(qr).data)
