from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status

from apps.qrcodes.models import QRCode
from apps.scans.models import ScanLog

from .services import get_client_ip
from .serializers import (
    QRCodeSerializer,
    QRCodeCreateSerializer,
    QRCodeClaimSerializer,
)


def _get_location_data(house):
    """Helper to format location data consistently"""
    return {
        "region": {
            "id": house.mahalla.district.region.id,
            "name": house.mahalla.district.region.name,
        },
        "district": {
            "id": house.mahalla.district.id,
            "name": house.mahalla.district.name,
        },
        "mahalla": {
            "id": house.mahalla.id,
            "name": house.mahalla.name,
        },
    }


def _get_owner_data(owner, include_private=False):
    """Helper to format owner data based on access level"""
    data = {
        "first_name": owner.first_name,
        "last_name": owner.last_name,
        "phone": owner.phone,
    }

    if include_private:
        data.update(
            {
                "passport_id": owner.passport_id,
                "address": owner.address,
            }
        )

    return data


class ScanQRCodeView(APIView):
    """Scan QR code by UUID - Main endpoint for all users"""

    permission_classes = [IsAuthenticated]

    def get(self, request, uuid):
        try:
            qr = QRCode.objects.select_related(
                "house__owner",
                "house__mahalla__district__region",
            ).get(uuid=uuid)
        except QRCode.DoesNotExist:
            return Response(
                {"error": "QR code not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Log scan and save UUID to user (for all cases)
        ScanLog.objects.create(
            qr=qr, scanned_by=request.user, ip_address=get_client_ip(request)
        )
        request.user.scanned_qr_code = qr.uuid
        request.user.save(update_fields=["scanned_qr_code"])

        # Unclaimed house - user can claim it
        if not qr.house.owner:
            return Response(
                {
                    "status": "unclaimed",
                    "message": "This house has no owner yet. You can claim it.",
                    "qr": {
                        "id": qr.id,
                        "uuid": qr.uuid,
                    },
                    "house": {
                        "address": qr.house.address,
                        "number": qr.house.house_number,
                        **_get_location_data(qr.house),
                    },
                }
            )

        # Determine access level based on user role
        user_role = getattr(request.user, "role", "user")
        # User can see private info if they own the house or if they are admin/government
        is_owner = qr.house.owner == request.user
        include_private = is_owner or user_role in [
            "government",
            "mahalla_admin",
            "super_admin",
        ]

        return Response(
            {
                "status": "claimed",
                "owner": _get_owner_data(qr.house.owner, include_private),
                "house": {
                    "address": qr.house.address,
                    "number": qr.house.house_number,
                    **_get_location_data(qr.house),
                },
            }
        )


class QRCodeListAPIView(generics.ListAPIView):
    """List QR codes based on user permissions"""

    permission_classes = [IsAuthenticated]
    serializer_class = QRCodeSerializer

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "role", None)

        if not role:
            return QRCode.objects.none()

        queryset = QRCode.objects.select_related("house__owner", "house__mahalla")

        # Users see only unclaimed houses
        if role == "user":
            return queryset.filter(house__owner__isnull=True)

        # Mahalla admin sees their neighborhood
        if role == "mahalla_admin" and hasattr(user, "mahalla"):
            return queryset.filter(house__mahalla=user.mahalla)

        # Super admin and government see all
        return queryset


class QRCodeCreateAPIView(generics.CreateAPIView):
    """Create new QR code for a house"""

    permission_classes = [IsAuthenticated]
    serializer_class = QRCodeCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        qr_code = serializer.save()

        response_serializer = QRCodeSerializer(qr_code)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class QRCodeDetailAPIView(generics.RetrieveAPIView):
    """Get single QR code details"""

    permission_classes = [IsAuthenticated]
    serializer_class = QRCodeSerializer
    lookup_field = "uuid"
    lookup_url_kwarg = "uuid"

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "role", None)

        if not role:
            return QRCode.objects.none()

        queryset = QRCode.objects.select_related("house__owner", "house__mahalla")

        # Regular users see only their own houses (where they are owner)
        if role == "user":
            return queryset.filter(house__owner=user)

        # Mahalla admin sees their neighborhood
        if role == "mahalla_admin" and hasattr(user, "mahalla"):
            return queryset.filter(house__mahalla=user.mahalla)

        # Super admin and government see all
        return queryset


class ClaimHouseView(APIView):
    """Claim house ownership after scanning QR code"""

    permission_classes = [IsAuthenticated]

    def post(self, request, uuid):
        try:
            qr = QRCode.objects.select_related("house__mahalla").get(uuid=uuid)
        except QRCode.DoesNotExist:
            return Response(
                {"error": "QR code not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if already claimed
        if qr.house.owner:
            return Response(
                {"error": "This house is already claimed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate and save user data
        serializer = QRCodeClaimSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Update user info (keep existing role - don't change to owner)
        user = request.user
        user.first_name = serializer.validated_data["first_name"]
        user.last_name = serializer.validated_data["last_name"]
        user.passport_id = serializer.validated_data["passport_id"]
        user.address = serializer.validated_data["address"]
        # Don't change role - user stays as "user"
        user.save()

        # Assign house ownership
        qr.house.owner = user
        qr.house.save()

        # Log the claim
        ScanLog.objects.create(
            qr=qr, scanned_by=user, ip_address=get_client_ip(request)
        )

        return Response(
            {
                "message": "House claimed successfully",
                "house": {
                    "id": qr.house.id,
                    "address": qr.house.address,
                    "number": qr.house.house_number,
                    "mahalla": qr.house.mahalla.name,
                },
                "owner": {
                    "phone": user.phone,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
                "qr": {
                    "id": qr.id,
                    "uuid": qr.uuid,
                },
            }
        )
