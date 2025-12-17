from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.qrcodes.models import QRCode
from apps.scans.models import ScanLog

from .services import get_client_ip


class QRScanAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, qr_id):
        try:
            qr = QRCode.objects.select_related(
                "house", "house__owner", "house__mahalla"
            ).get(id=qr_id)
        except QRCode.DoesNotExist:
            return Response({"error": "QR code not found"}, status=404)

        ScanLog.objects.create(
            qr=qr, scanned_by=request.user, ip_address=get_client_ip(request)
        )

        owner = qr.house.owner
        user = request.user

        if user.role == "user":
            return Response(
                {
                    "first_name": owner.first_name,
                    "last_name": owner.last_name,
                    "phone": owner.phone,
                }
            )

        if user.role == "owner":
            return Response(
                {
                    "first_name": owner.first_name,
                    "last_name": owner.last_name,
                    "phone": owner.phone,
                    "passport_id": owner.passport_id,
                    "address": owner.address,
                    "house_address": qr.house.address,
                    "mahalla": qr.house.mahalla.name,
                }
            )

        if user.role in ["government", "mahalla_admin", "super_admin"]:
            return Response(
                {
                    "first_name": owner.first_name,
                    "last_name": owner.last_name,
                    "phone": owner.phone,
                    "passport_id": owner.passport_id,
                    "address": owner.address,
                    "house_address": qr.house.address,
                    "mahalla": qr.house.mahalla.name,
                }
            )

        return Response({"detail": "Access denied"}, status=403)
