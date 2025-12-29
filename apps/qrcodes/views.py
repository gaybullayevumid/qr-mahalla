from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
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


def _get_owner_data(owner, user_role="anonymous", is_owner=False):
    """Helper to format owner data based on access level - role-based"""
    # Minimal ma'lumot (non-authenticated yoki oddiy user)
    data = {
        "id": owner.id,
        "first_name": owner.first_name,
        "last_name": owner.last_name,
        "phone": owner.phone,
    }

    # To'liq ma'lumot (admin yoki o'z uy egasi)
    if user_role in ["admin", "gov", "leader"] or is_owner:
        data.update(
            {
                "role": owner.role,
                "is_verified": owner.is_verified,
            }
        )

    return data


class QRCodeScanAPIView(APIView):
    """
    POST endpoint for QR code scanning
    Frontend sends UUID, backend returns house and owner info based on role
    Supports both authenticated and non-authenticated users
    """

    permission_classes = [AllowAny]

    def extract_uuid(self, data):
        """Extract UUID from various input formats"""
        if not data:
            return None

        data = str(data).strip()

        # If it's a full URL (from phone camera scan)
        if "t.me/" in data or "telegram.me/" in data:
            # Extract from: https://t.me/qrmahallabot/start?startapp=QR_KEY_abc123def456
            if "QR_KEY_" in data:
                parts = data.split("QR_KEY_")
                if len(parts) > 1:
                    return parts[1].strip()

        # If it's just the UUID (16 chars hex)
        if len(data) == 16:
            return data

        return data

    def post(self, request):
        raw_data = (
            request.data.get("uuid")
            or request.data.get("qr_code")
            or request.data.get("url")
        )

        if not raw_data:
            return Response(
                {
                    "error": "QR code data is required. Send 'uuid', 'qr_code', or 'url' parameter."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Extract UUID from input
        uuid = self.extract_uuid(raw_data)

        if not uuid:
            return Response(
                {"error": "Invalid QR code format"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Find QR code
        try:
            qr = QRCode.objects.select_related(
                "house__owner",
                "house__mahalla__district__region",
            ).get(uuid=uuid)
        except QRCode.DoesNotExist:
            return Response(
                {"error": "QR code not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Log scan if user is authenticated
        if request.user and request.user.is_authenticated:
            ScanLog.objects.create(
                qr=qr, scanned_by=request.user, ip_address=get_client_ip(request)
            )
            # Save scanned UUID to user
            request.user.scanned_qr_code = qr.uuid
            request.user.save(update_fields=["scanned_qr_code"])

        # Get user role (anonymous if not authenticated)
        user_role = "anonymous"
        is_owner = False

        if request.user and request.user.is_authenticated:
            user_role = getattr(request.user, "role", "user")
            is_owner = (
                qr.house and qr.house.owner == request.user if qr.house else False
            )

        # QR kod house ga bog'lanmagan yoki house egasi yo'q
        if not qr.house or not qr.house.owner:
            response_data = {
                "status": "unclaimed",
                "message": (
                    "Bu QR kod hali biriktirilmagan. Siz uyingiz ma'lumotlarini kiritib claim qilishingiz mumkin."
                    if user_role != "anonymous"
                    else "Bu QR kod hali biriktirilmagan."
                ),
                "qr": {
                    "id": qr.id,
                    "uuid": qr.uuid,
                    "qr_url": qr.get_qr_url(),
                },
            }

            # Agar house bor bo'lsa ma'lumotini qo'shamiz
            if qr.house:
                response_data["house"] = {
                    "id": qr.house.id,
                    "address": qr.house.address,
                    "house_number": qr.house.house_number,
                    **_get_location_data(qr.house),
                }
            else:
                response_data["house"] = None

            response_data["owner"] = None

            # Add claim URL only for authenticated users
            if user_role != "anonymous":
                response_data["can_claim"] = True
                response_data["claim_url"] = f"/api/qrcodes/claim/{uuid}/"
            else:
                response_data["can_claim"] = False
                response_data["message"] = (
                    "Bu uyning egasi yo'q. Claim qilish uchun login qiling."
                )

            return Response(response_data)

        # House has owner - return owner info based on role
        return Response(
            {
                "status": "claimed",
                "qr": {
                    "id": qr.id,
                    "uuid": qr.uuid,
                    "qr_url": qr.get_qr_url(),
                },
                "house": {
                    "id": qr.house.id,
                    "address": qr.house.address,
                    "house_number": qr.house.house_number,
                    **_get_location_data(qr.house),
                },
                "owner": _get_owner_data(qr.house.owner, user_role, is_owner),
                "is_owner": is_owner,
            }
        )


class ScanQRCodeView(APIView):
    """Scan QR code by UUID - Main endpoint for all users"""

    permission_classes = [AllowAny]

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

        # Log scan and save UUID to user (only if authenticated)
        if request.user and request.user.is_authenticated:
            ScanLog.objects.create(
                qr=qr, scanned_by=request.user, ip_address=get_client_ip(request)
            )
            request.user.scanned_qr_code = qr.uuid
            request.user.save(update_fields=["scanned_qr_code"])

        # Get user role
        user_role = "anonymous"
        is_owner = False
        if request.user and request.user.is_authenticated:
            user_role = getattr(request.user, "role", "user")
            if qr.house and qr.house.owner:
                is_owner = qr.house.owner == request.user

        # QR code has no house or house has no owner - user can claim it
        if not qr.house or not qr.house.owner:
            response_data = {
                "status": "unclaimed",
                "message": (
                    "Bu QR kod hali biriktirilmagan. Siz uyingiz ma'lumotlarini kiritib claim qilishingiz mumkin."
                    if user_role != "anonymous"
                    else "Bu uyning egasi yo'q. Claim qilish uchun login qiling."
                ),
                "qr": {
                    "id": qr.id,
                    "uuid": qr.uuid,
                    "qr_url": qr.get_qr_url(),
                },
            }

            # Add house info if exists
            if qr.house:
                response_data["house"] = {
                    "id": qr.house.id,
                    "address": qr.house.address,
                    "house_number": qr.house.house_number,
                    **_get_location_data(qr.house),
                }
            else:
                response_data["house"] = None

            response_data["owner"] = None

            # Add claim URL only for authenticated users
            if user_role != "anonymous":
                response_data["can_claim"] = True
                response_data["claim_url"] = f"/api/qrcodes/claim/{uuid}/"
            else:
                response_data["can_claim"] = False

            return Response(response_data)

        return Response(
            {
                "status": "claimed",
                "qr": {
                    "id": qr.id,
                    "uuid": qr.uuid,
                    "qr_url": qr.get_qr_url(),
                },
                "house": {
                    "id": qr.house.id,
                    "address": qr.house.address,
                    "house_number": qr.house.house_number,
                    **_get_location_data(qr.house),
                },
                "owner": _get_owner_data(qr.house.owner, user_role, is_owner),
                "is_owner": is_owner,
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

        # Clients see only unclaimed QR codes (no house or no owner)
        if role == "client":
            from django.db.models import Q

            return queryset.filter(Q(house__isnull=True) | Q(house__owner__isnull=True))

        # Leader (mahalla admin) sees their neighborhood
        if role == "leader" and hasattr(user, "mahalla"):
            return queryset.filter(house__mahalla=user.mahalla)

        # Admin and government see all
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

        # Regular clients see unclaimed QR codes and their own houses
        if role == "client":
            from django.db.models import Q

            return queryset.filter(
                Q(house__isnull=True)
                | Q(house__owner__isnull=True)
                | Q(house__owner=user)
            )

        # Leader (mahalla admin) sees their neighborhood
        if role == "leader" and hasattr(user, "mahalla"):
            return queryset.filter(house__mahalla=user.mahalla)

        # Admin and government see all
        return queryset


class ClaimHouseView(APIView):
    """Claim house ownership after scanning QR code"""

    permission_classes = [IsAuthenticated]

    def post(self, request, uuid):
        from django.db import transaction, IntegrityError
        from apps.regions.models import Mahalla
        from apps.houses.models import House

        try:
            qr = QRCode.objects.select_related("house__mahalla").get(uuid=uuid)
        except QRCode.DoesNotExist:
            return Response(
                {"error": "QR code not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if QR already has a house with owner
        if qr.house and qr.house.owner:
            return Response(
                {"error": "This house is already claimed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate claim data (user + house info)
        serializer = QRCodeClaimSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        try:
            mahalla = Mahalla.objects.get(id=serializer.validated_data["mahalla"])
        except Mahalla.DoesNotExist:
            return Response(
                {"error": "Mahalla not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Use atomic transaction to prevent race conditions
        try:
            with transaction.atomic():
                # Re-fetch QR code with lock to prevent concurrent claims
                qr = QRCode.objects.select_for_update().get(uuid=uuid)

                # Double-check after lock
                if qr.house and qr.house.owner:
                    return Response(
                        {"error": "This house is already claimed"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Update user info
                user.first_name = serializer.validated_data["first_name"]
                user.last_name = serializer.validated_data["last_name"]
                user.save(update_fields=["first_name", "last_name"])

                if qr.house:
                    # Update existing house
                    qr.house.address = serializer.validated_data["address"]
                    qr.house.house_number = serializer.validated_data["house_number"]
                    qr.house.mahalla = mahalla
                    qr.house.owner = user
                    qr.house.save()
                    house = qr.house
                else:
                    # Create new house and link to QR code
                    house = House.objects.create(
                        address=serializer.validated_data["address"],
                        house_number=serializer.validated_data["house_number"],
                        mahalla=mahalla,
                        owner=user,
                    )

                    # Link QR to house
                    qr.house = house
                    qr.save()

                # Log the claim
                ScanLog.objects.create(
                    qr=qr, scanned_by=user, ip_address=get_client_ip(request)
                )

                return Response(
                    {
                        "message": "House claimed successfully",
                        "house": {
                            "id": house.id,
                            "address": house.address,
                            "number": house.house_number,
                            "mahalla": house.mahalla.name,
                            "district": house.mahalla.district.name,
                            "region": house.mahalla.district.region.name,
                        },
                        "owner": {
                            "phone": user.phone,
                            "first_name": user.first_name,
                            "last_name": user.last_name,
                            "role": user.role,
                        },
                        "qr": {
                            "id": qr.id,
                            "uuid": qr.uuid,
                            "qr_url": qr.get_qr_url(),
                        },
                    }
                )

        except IntegrityError as e:
            return Response(
                {
                    "error": "Database integrity error. This house may already have a QR code or there's a duplicate entry.",
                    "detail": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "error": "An unexpected error occurred while claiming the house",
                    "detail": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
