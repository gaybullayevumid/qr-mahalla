from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status

from apps.qrcodes.models import QRCode
from apps.scans.models import ScanLog
from apps.houses.models import House

from .services import get_client_ip
from .serializers import QRCodeSerializer, QRCodeCreateSerializer, QRCodeClaimSerializer


class QRScanAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, qr_id):
        try:
            qr = QRCode.objects.select_related(
                "house", "house__owner", "house__mahalla"
            ).get(id=qr_id)
        except QRCode.DoesNotExist:
            return Response({"error": "QR code not found"}, status=404)

        # Check if house has no owner - needs to be claimed
        if not qr.house.owner:
            return Response(
                {
                    "status": "unclaimed",
                    "message": "This house has no owner yet",
                    "house_address": qr.house.address,
                    "mahalla": qr.house.mahalla.name,
                    "house_number": qr.house.house_number,
                },
                status=200,
            )

        ScanLog.objects.create(
            qr=qr, scanned_by=request.user, ip_address=get_client_ip(request)
        )

        owner = qr.house.owner
        user = request.user

        if not user.is_authenticated or not hasattr(user, "role"):
            return Response({"detail": "Authentication required"}, status=401)

        if user.role == "user":
            return Response(
                {
                    "status": "claimed",
                    "first_name": owner.first_name,
                    "last_name": owner.last_name,
                    "phone": owner.phone,
                }
            )

        if user.role == "owner":
            return Response(
                {
                    "status": "claimed",
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
                    "status": "claimed",
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

        if not user.is_authenticated or not hasattr(user, "role"):
            return queryset.none()

        # Filter based on user role
        if user.role == "owner":
            # Owner can see only their houses' QR codes
            queryset = queryset.filter(house__owner=user)
        elif user.role == "mahalla_admin":
            # Neighborhood admin can see only their neighborhood's QR codes
            queryset = queryset.filter(house__mahalla=user.mahalla)
        # super_admin, government can see all QR codes

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

        # Return full response data
        response_serializer = QRCodeSerializer(qr_code)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class QRCodeDetailAPIView(generics.RetrieveAPIView):
    """
    Get single QR code details (GET)
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

        if not user.is_authenticated or not hasattr(user, "role"):
            return queryset.none()

        # Filter based on user role
        if user.role == "owner":
            queryset = queryset.filter(house__owner=user)
        elif user.role == "mahalla_admin":
            queryset = queryset.filter(house__mahalla=user.mahalla)

        return queryset


class QRCodeClaimAPIView(APIView):
    """
    Claim house ownership via QR code (POST)
    User scans QR code and submits their information to claim the house
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, qr_id):
        try:
            qr = QRCode.objects.select_related("house").get(id=qr_id)
        except QRCode.DoesNotExist:
            return Response(
                {"error": "QR code not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if house already has an owner
        if qr.house.owner:
            return Response(
                {"error": "This house already has an owner"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate claim data
        serializer = QRCodeClaimSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Update current user's information
        user = request.user
        user.first_name = serializer.validated_data["first_name"]
        user.last_name = serializer.validated_data["last_name"]
        user.passport_id = serializer.validated_data["passport_id"]
        user.address = serializer.validated_data["address"]
        user.role = "owner"
        user.save()

        # Assign house to user
        qr.house.owner = user
        qr.house.save()

        # Create scan log
        ScanLog.objects.create(
            qr=qr, scanned_by=user, ip_address=get_client_ip(request)
        )

        return Response(
            {
                "message": "House claimed successfully",
                "house": {
                    "id": str(qr.house.id),
                    "address": qr.house.address,
                    "house_number": qr.house.house_number,
                    "mahalla": qr.house.mahalla.name,
                },
                "owner": {
                    "phone": user.phone,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
            },
            status=status.HTTP_200_OK,
        )
