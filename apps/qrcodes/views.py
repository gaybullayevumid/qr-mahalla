from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from django.utils import timezone

from apps.qrcodes.models import QRCode
from apps.scans.models import ScanLog
from apps.houses.models import House

from .services import get_client_ip
from .serializers import (
    QRCodeSerializer,
    QRCodeCreateSerializer,
    QRCodeClaimSerializer,
    QRCodeDeliverySerializer,
)


class QRScanAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, qr_id):
        try:
            qr = QRCode.objects.select_related(
                "house",
                "house__owner",
                "house__mahalla",
                "house__mahalla__district",
                "house__mahalla__district__region",
            ).get(id=qr_id)
        except QRCode.DoesNotExist:
            return Response({"error": "QR code not found"}, status=404)

        # Check if house has no owner - needs to be claimed
        if not qr.house.owner:
            return Response(
                {
                    "status": "unclaimed",
                    "is_claimed": False,
                    "can_claim": True,
                    "message": "This house has no owner yet",
                    "qr_id": qr.id,
                    "claim_url": f"/api/qrcode/claim/{qr.id}/",
                    "house_address": qr.house.address,
                    "house_number": qr.house.house_number,
                    "region": {
                        "id": qr.house.mahalla.district.region.id,
                        "name": qr.house.mahalla.district.region.name,
                    },
                    "district": {
                        "id": qr.house.mahalla.district.id,
                        "name": qr.house.mahalla.district.name,
                    },
                    "mahalla": {
                        "id": qr.house.mahalla.id,
                        "name": qr.house.mahalla.name,
                    },
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
                    "is_claimed": True,
                    "can_claim": False,
                    "first_name": owner.first_name,
                    "last_name": owner.last_name,
                    "phone": owner.phone,
                    "house_address": qr.house.address,
                    "region": {
                        "id": qr.house.mahalla.district.region.id,
                        "name": qr.house.mahalla.district.region.name,
                    },
                    "district": {
                        "id": qr.house.mahalla.district.id,
                        "name": qr.house.mahalla.district.name,
                    },
                    "mahalla": {
                        "id": qr.house.mahalla.id,
                        "name": qr.house.mahalla.name,
                    },
                }
            )

        if user.role == "owner":
            return Response(
                {
                    "status": "claimed",
                    "is_claimed": True,
                    "can_claim": False,
                    "first_name": owner.first_name,
                    "last_name": owner.last_name,
                    "phone": owner.phone,
                    "passport_id": owner.passport_id,
                    "address": owner.address,
                    "house_address": qr.house.address,
                    "region": {
                        "id": qr.house.mahalla.district.region.id,
                        "name": qr.house.mahalla.district.region.name,
                    },
                    "district": {
                        "id": qr.house.mahalla.district.id,
                        "name": qr.house.mahalla.district.name,
                    },
                    "mahalla": {
                        "id": qr.house.mahalla.id,
                        "name": qr.house.mahalla.name,
                    },
                }
            )

        if user.role in ["government", "mahalla_admin", "super_admin"]:
            return Response(
                {
                    "status": "claimed",
                    "is_claimed": True,
                    "can_claim": False,
                    "first_name": owner.first_name,
                    "last_name": owner.last_name,
                    "phone": owner.phone,
                    "passport_id": owner.passport_id,
                    "address": owner.address,
                    "house_address": qr.house.address,
                    "region": {
                        "id": qr.house.mahalla.district.region.id,
                        "name": qr.house.mahalla.district.region.name,
                    },
                    "district": {
                        "id": qr.house.mahalla.district.id,
                        "name": qr.house.mahalla.district.name,
                    },
                    "mahalla": {
                        "id": qr.house.mahalla.id,
                        "name": qr.house.mahalla.name,
                    },
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

        # Regular users can see only unclaimed QR codes
        if user.role == "user":
            return queryset.filter(house__owner__isnull=True)

        # Filter based on user role
        if user.role == "owner":
            # Owner can see only their houses' QR codes
            queryset = queryset.filter(house__owner=user)
        elif user.role == "mahalla_admin":
            # Neighborhood admin can see only their neighborhood's QR codes
            queryset = queryset.filter(house__mahalla=user.mahalla)
        # super_admin, government can see all QR codes

        return queryset
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


class QRCodeMarkDeliveredAPIView(APIView):
    """
    Mark QR code as delivered to house owner
    Only super_admin and mahalla_admin can mark as delivered
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Check if user has permission (only super_admin and mahalla_admin)
        if user.role not in ["super_admin", "mahalla_admin"]:
            return Response(
                {"error": "Only admins can mark QR codes as delivered"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = QRCodeDeliverySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        qr_id = serializer.validated_data["qr_id"]

        try:
            qr = QRCode.objects.get(id=qr_id)
        except QRCode.DoesNotExist:
            return Response(
                {"error": "QR code not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if already delivered
        if qr.is_delivered:
            return Response(
                {
                    "error": "QR code already marked as delivered",
                    "delivered_at": qr.delivered_at,
                    "delivered_by": (
                        f"{qr.delivered_by.first_name} {qr.delivered_by.last_name}"
                        if qr.delivered_by
                        else None
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mark as delivered
        qr.is_delivered = True
        qr.delivered_at = timezone.now()
        qr.delivered_by = user
        qr.save()

        return Response(
            {
                "message": "QR code marked as delivered successfully",
                "qr_code": {
                    "id": qr.id,
                    "house_address": qr.house.address,
                    "is_delivered": qr.is_delivered,
                    "delivered_at": qr.delivered_at,
                    "delivered_by": f"{user.first_name} {user.last_name}".strip()
                    or user.phone,
                },
            },
            status=status.HTTP_200_OK,
        )


class QRCodeUnmarkDeliveredAPIView(APIView):
    """
    Unmark QR code delivery (in case of mistake)
    Only super_admin can unmark
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Only super_admin can unmark
        if user.role != "super_admin":
            return Response(
                {"error": "Only super admin can unmark delivery"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = QRCodeDeliverySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        qr_id = serializer.validated_data["qr_id"]

        try:
            qr = QRCode.objects.get(id=qr_id)
        except QRCode.DoesNotExist:
            return Response(
                {"error": "QR code not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if not delivered
        if not qr.is_delivered:
            return Response(
                {"error": "QR code is not marked as delivered"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Unmark delivery
        qr.is_delivered = False
        qr.delivered_at = None
        qr.delivered_by = None
        qr.save()

        return Response(
            {
                "message": "QR code delivery status removed successfully",
                "qr_code": {
                    "id": qr.id,
                    "house_address": qr.house.address,
                    "is_delivered": qr.is_delivered,
                },
            },
            status=status.HTTP_200_OK,
        )


class QRScanByUUIDAPIView(APIView):
    """
    Scan QR code using UUID (from QR code itself)
    This is the main endpoint for regular users scanning QR codes
    URL: /api/qrcodes/scan-uuid/{uuid}/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, uuid):
        try:
            qr = QRCode.objects.select_related(
                "house",
                "house__owner",
                "house__mahalla",
                "house__mahalla__district",
                "house__mahalla__district__region",
            ).get(uuid=uuid)
        except QRCode.DoesNotExist:
            return Response(
                {"error": "QR code not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if house has no owner - needs to be claimed
        if not qr.house.owner:
            return Response(
                {
                    "status": "unclaimed",
                    "is_claimed": False,
                    "can_claim": True,
                    "message": "This house has no owner yet. You can claim it.",
                    "qr_id": qr.id,
                    "uuid": qr.uuid,
                    "claim_url": f"/api/qrcodes/claim-uuid/{qr.uuid}/",
                    "house_address": qr.house.address,
                    "house_number": qr.house.house_number,
                    "region": {
                        "id": qr.house.mahalla.district.region.id,
                        "name": qr.house.mahalla.district.region.name,
                    },
                    "district": {
                        "id": qr.house.mahalla.district.id,
                        "name": qr.house.mahalla.district.name,
                    },
                    "mahalla": {
                        "id": qr.house.mahalla.id,
                        "name": qr.house.mahalla.name,
                    },
                },
                status=status.HTTP_200_OK,
            )

        # Log the scan
        ScanLog.objects.create(
            qr=qr, scanned_by=request.user, ip_address=get_client_ip(request)
        )

        owner = qr.house.owner
        user = request.user

        if not user.is_authenticated or not hasattr(user, "role"):
            return Response(
                {"detail": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Return info based on user role
        if user.role == "user":
            return Response(
                {
                    "status": "claimed",
                    "is_claimed": True,
                    "can_claim": False,
                    "first_name": owner.first_name,
                    "last_name": owner.last_name,
                    "phone": owner.phone,
                    "house_address": qr.house.address,
                    "region": {
                        "id": qr.house.mahalla.district.region.id,
                        "name": qr.house.mahalla.district.region.name,
                    },
                    "district": {
                        "id": qr.house.mahalla.district.id,
                        "name": qr.house.mahalla.district.name,
                    },
                    "mahalla": {
                        "id": qr.house.mahalla.id,
                        "name": qr.house.mahalla.name,
                    },
                }
            )

        if user.role == "owner":
            return Response(
                {
                    "status": "claimed",
                    "is_claimed": True,
                    "can_claim": False,
                    "first_name": owner.first_name,
                    "last_name": owner.last_name,
                    "phone": owner.phone,
                    "passport_id": owner.passport_id,
                    "address": owner.address,
                    "house_address": qr.house.address,
                    "mahalla": qr.house.mahalla.name,
                    "district": qr.house.mahalla.district.name,
                    "region": qr.house.mahalla.district.region.name,
                }
            )

        if user.role in ["government", "mahalla_admin", "super_admin"]:
            return Response(
                {
                    "status": "claimed",
                    "is_claimed": True,
                    "can_claim": False,
                    "first_name": owner.first_name,
                    "last_name": owner.last_name,
                    "phone": owner.phone,
                    "passport_id": owner.passport_id,
                    "address": owner.address,
                    "house_address": qr.house.address,
                    "region": {
                        "id": qr.house.mahalla.district.region.id,
                        "name": qr.house.mahalla.district.region.name,
                    },
                    "district": {
                        "id": qr.house.mahalla.district.id,
                        "name": qr.house.mahalla.district.name,
                    },
                    "mahalla": {
                        "id": qr.house.mahalla.id,
                        "name": qr.house.mahalla.name,
                    },
                }
            )

        return Response({"detail": "Access denied"}, status=status.HTTP_403_FORBIDDEN)


class QRCodeClaimByUUIDAPIView(APIView):
    """
    Claim house ownership via QR code UUID
    Regular user scans QR code and submits their information to claim the house
    URL: /api/qrcodes/claim-uuid/{uuid}/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, uuid):
        try:
            qr = QRCode.objects.select_related("house", "house__mahalla").get(uuid=uuid)
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
                "status": "success",
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
                "qr_code": {
                    "id": qr.id,
                    "uuid": qr.uuid,
                },
            },
            status=status.HTTP_200_OK,
        )
