from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status

from apps.qrcodes.models import QRCode
from apps.scans.models import ScanLog

from .services import get_client_ip
from .serializers import QRCodeSerializer, QRCodeCreateSerializer


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

        if not user.is_authenticated or not hasattr(user, 'role'):
            return Response({"detail": "Authentication required"}, status=401)

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


class QRCodeListAPIView(generics.ListAPIView):
    """
    QR kodlar ro'yxatini olish (GET)
    """

    permission_classes = [IsAuthenticated]
    serializer_class = QRCodeSerializer
    queryset = QRCode.objects.select_related(
        "house", "house__owner", "house__mahalla"
    ).all()

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        if not user.is_authenticated or not hasattr(user, 'role'):
            return queryset.none()

        # Foydalanuvchi roliga qarab filterlash
        if user.role == "owner":
            # Uy egasi faqat o'z uylarining QR kodlarini ko'ra oladi
            queryset = queryset.filter(house__owner=user)
        elif user.role == "mahalla_admin":
            # Mahalla admin faqat o'z mahallasining QR kodlarini ko'ra oladi
            queryset = queryset.filter(house__mahalla=user.mahalla)
        # super_admin, government barcha QR kodlarni ko'ra oladi

        return queryset


class QRCodeCreateAPIView(generics.CreateAPIView):
    """
    Yangi QR kod yaratish (POST)
    """

    permission_classes = [IsAuthenticated]
    serializer_class = QRCodeCreateSerializer
    queryset = QRCode.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        qr_code = serializer.save()

        # Response uchun to'liq ma'lumot qaytarish
        response_serializer = QRCodeSerializer(qr_code)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class QRCodeDetailAPIView(generics.RetrieveAPIView):
    """
    Bitta QR kod ma'lumotini olish (GET)
    """

    permission_classes = [IsAuthenticated]
    serializer_class = QRCodeSerializer
    queryset = QRCode.objects.select_related(
        "house", "house__owner", "house__mahalla"
    ).all()
    lookup_field = "id"
    lookup_url_kwarg = "qr_id"

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        if not user.is_authenticated or not hasattr(user, 'role'):
            return queryset.none()

        # Foydalanuvchi roliga qarab filterlash
        if user.role == "owner":
            queryset = queryset.filter(house__owner=user)
        elif user.role == "mahalla_admin":
            queryset = queryset.filter(house__mahalla=user.mahalla)

        return queryset
