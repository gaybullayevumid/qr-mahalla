from typing import Dict, Any, Optional

from django.db import transaction, IntegrityError
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, status
from rest_framework.request import Request

from apps.qrcodes.models import QRCode
from apps.scans.models import ScanLog
from apps.regions.models import Mahalla
from apps.houses.models import House

from .services import get_client_ip
from .serializers import (
    QRCodeSerializer,
    QRCodeCreateSerializer,
    QRCodeClaimSerializer,
)


# Constants
ADMIN_ROLES = ["admin", "gov", "leader"]
ANONYMOUS_ROLE = "anonymous"
CLIENT_ROLE = "client"
LEADER_ROLE = "leader"


def _get_location_data(house) -> Dict[str, Dict[str, Any]]:
    """
    Format location data consistently.

    Args:
        house: House object with related mahalla, district, and region

    Returns:
        Dictionary containing region, district, and mahalla info
    """
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


def _get_owner_data(
    owner, user_role: str = ANONYMOUS_ROLE, is_owner: bool = False
) -> Dict[str, Any]:
    """
    Format owner data based on access level.

    Returns minimal data for anonymous/regular users,
    full data for admins and house owners.

    Args:
        owner: User object who owns the house
        user_role: Role of the requesting user
        is_owner: Whether requesting user is the house owner

    Returns:
        Dictionary containing owner information based on access level
    """
    # Minimal info (non-authenticated or regular user)
    data = {
        "id": owner.id,
        "first_name": owner.first_name,
        "last_name": owner.last_name,
        "phone": owner.phone,
    }

    # Full info (admin or house owner)
    if user_role in ADMIN_ROLES or is_owner:
        data.update(
            {
                "role": owner.role,
                "is_verified": owner.is_verified,
            }
        )

    return data


def _get_user_role_and_ownership(request: Request, qr: QRCode) -> tuple[str, bool]:
    """
    Determine user role and ownership status.

    Args:
        request: HTTP request object
        qr: QRCode object being accessed

    Returns:
        Tuple of (user_role, is_owner)
    """
    user_role = ANONYMOUS_ROLE
    is_owner = False

    if request.user and request.user.is_authenticated:
        user_role = getattr(request.user, "role", "user")
        if qr.house and qr.house.owner:
            is_owner = qr.house.owner == request.user

    return user_role, is_owner


def _log_qr_scan(request: Request, qr: QRCode) -> None:
    """
    Log QR code scan and save UUID to user profile.

    Args:
        request: HTTP request object
        qr: QRCode object being scanned
    """
    if request.user and request.user.is_authenticated:
        ScanLog.objects.create(
            qr=qr, scanned_by=request.user, ip_address=get_client_ip(request)
        )
        request.user.scanned_qr_code = qr.uuid
        request.user.save(update_fields=["scanned_qr_code"])


def _get_unclaimed_response(qr: QRCode, user_role: str) -> Dict[str, Any]:
    """
    Build response for unclaimed QR codes.

    Args:
        qr: QRCode object
        user_role: Role of the requesting user

    Returns:
        Response data dictionary
    """
    response_data = {
        "status": "unclaimed",
        "message": (
            "Bu QR kod hali biriktirilmagan. Siz uyingiz ma'lumotlarini kiritib claim qilishingiz mumkin."
            if user_role != ANONYMOUS_ROLE
            else "Bu QR kod hali biriktirilmagan."
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
    if user_role != ANONYMOUS_ROLE:
        response_data["can_claim"] = True
        response_data["claim_url"] = f"/api/qrcodes/claim/{qr.uuid}/"
    else:
        response_data["can_claim"] = False
        response_data["message"] = (
            "Bu uyning egasi yo'q. Claim qilish uchun login qiling."
        )

    return response_data


def _get_claimed_response(qr: QRCode, user_role: str, is_owner: bool) -> Dict[str, Any]:
    """
    Build response for claimed QR codes.

    Args:
        qr: QRCode object
        user_role: Role of the requesting user
        is_owner: Whether requesting user owns the house

    Returns:
        Response data dictionary
    """
    return {
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


class QRCodeScanAPIView(APIView):
    """
    POST endpoint for QR code scanning.

    Accepts QR code data in various formats (UUID, URL, Telegram link).
    Returns house and owner info based on user role and ownership.
    Supports both authenticated and anonymous users.
    """

    permission_classes = [AllowAny]

    def extract_uuid(self, data: Any) -> Optional[str]:
        """
        Extract UUID from various input formats.

        Args:
            data: Raw input data (URL, UUID, etc.)

        Returns:
            Extracted UUID string or None
        """
        if not data:
            return None

        data = str(data).strip()

        # If it's a full URL (from phone camera scan)
        # Format: https://t.me/qrmahallabot/start?startapp=QR_KEY_abc123def456
        if "t.me/" in data or "telegram.me/" in data:
            if "QR_KEY_" in data:
                parts = data.split("QR_KEY_")
                if len(parts) > 1:
                    return parts[1].strip()

        # If it's just the UUID (16 chars hex)
        if len(data) == 16:
            return data

        return data

    def post(self, request: Request) -> Response:
        """Handle QR code scan request."""
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

        # Log scan
        _log_qr_scan(request, qr)

        # Get user role and ownership
        user_role, is_owner = _get_user_role_and_ownership(request, qr)

        # QR code not linked to house or house has no owner
        if not qr.house or not qr.house.owner:
            return Response(_get_unclaimed_response(qr, user_role))

        # House has owner - return based on role
        return Response(_get_claimed_response(qr, user_role, is_owner))


class ScanQRCodeView(APIView):
    """
    GET endpoint for QR code scanning by UUID.

    Main endpoint for all users to scan QR codes.
    Similar to QRCodeScanAPIView but uses GET method.
    """

    permission_classes = [AllowAny]

    def get(self, request: Request, uuid: str) -> Response:
        """Handle QR code scan via GET request."""
        try:
            qr = QRCode.objects.select_related(
                "house__owner",
                "house__mahalla__district__region",
            ).get(uuid=uuid)
        except QRCode.DoesNotExist:
            return Response(
                {"error": "QR code not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Log scan
        _log_qr_scan(request, qr)

        # Get user role and ownership
        user_role, is_owner = _get_user_role_and_ownership(request, qr)

        # QR code not linked to house or house has no owner
        if not qr.house or not qr.house.owner:
            return Response(_get_unclaimed_response(qr, user_role))

        # House has owner - return based on role
        return Response(_get_claimed_response(qr, user_role, is_owner))


class QRCodeListAPIView(generics.ListAPIView):
    """
    List QR codes based on user permissions.

    - Clients: See only unclaimed QR codes
    - Leaders: See QR codes in their mahalla
    - Admins/Gov: See all QR codes
    """

    permission_classes = [IsAuthenticated]
    serializer_class = QRCodeSerializer

    def get_queryset(self):
        """Filter QR codes based on user role."""
        user = self.request.user
        role = getattr(user, "role", None)

        if not role:
            return QRCode.objects.none()

        queryset = QRCode.objects.select_related("house__owner", "house__mahalla")

        # Clients see only unclaimed QR codes (no house or no owner)
        if role == CLIENT_ROLE:
            return queryset.filter(Q(house__isnull=True) | Q(house__owner__isnull=True))

        # Leaders see their neighborhood
        if role == LEADER_ROLE and hasattr(user, "mahalla"):
            return queryset.filter(house__mahalla=user.mahalla)

        # Admins and government see all
        return queryset


class QRCodeCreateAPIView(generics.CreateAPIView):
    """
    Create new QR code for a house.

    Only authenticated users can create QR codes.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = QRCodeCreateSerializer

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Create QR code and return full details."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        qr_code = serializer.save()

        response_serializer = QRCodeSerializer(qr_code)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class QRCodeDetailAPIView(generics.RetrieveAPIView):
    """
    Get single QR code details.

    Access control:
    - Clients: Unclaimed QR codes and their own houses
    - Leaders: QR codes in their neighborhood
    - Admins/Gov: All QR codes
    """

    permission_classes = [IsAuthenticated]
    serializer_class = QRCodeSerializer
    lookup_field = "uuid"
    lookup_url_kwarg = "uuid"

    def get_queryset(self):
        """Filter QR codes based on user role."""
        user = self.request.user
        role = getattr(user, "role", None)

        if not role:
            return QRCode.objects.none()

        queryset = QRCode.objects.select_related("house__owner", "house__mahalla")

        # Regular clients see unclaimed QR codes and their own houses
        if role == CLIENT_ROLE:
            return queryset.filter(
                Q(house__isnull=True)
                | Q(house__owner__isnull=True)
                | Q(house__owner=user)
            )

        # Leaders see their neighborhood
        if role == LEADER_ROLE and hasattr(user, "mahalla"):
            return queryset.filter(house__mahalla=user.mahalla)

        # Admins and government see all
        return queryset


class ClaimHouseView(APIView):
    """
    Claim house ownership after scanning QR code.

    Only authenticated users can claim houses.
    Uses atomic transactions to prevent race conditions.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, uuid: str) -> Response:
        """Handle house claim request."""
        # Find QR code
        try:
            qr = QRCode.objects.select_related("house__mahalla").get(uuid=uuid)
        except QRCode.DoesNotExist:
            return Response(
                {"error": "QR code not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if already claimed
        if qr.house and qr.house.owner:
            return Response(
                {"error": "This house is already claimed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate claim data
        serializer = QRCodeClaimSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        validated_data = serializer.validated_data

        # Find mahalla
        try:
            mahalla = Mahalla.objects.get(id=validated_data["mahalla"])
        except Mahalla.DoesNotExist:
            return Response(
                {"error": "Mahalla not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Use atomic transaction to prevent race conditions
        try:
            with transaction.atomic():
                # Re-fetch with lock
                qr = QRCode.objects.select_for_update().get(uuid=uuid)

                # Double-check after lock
                if qr.house and qr.house.owner:
                    return Response(
                        {"error": "This house is already claimed"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Update user info
                user.first_name = validated_data["first_name"]
                user.last_name = validated_data["last_name"]
                user.save(update_fields=["first_name", "last_name"])

                # Update or create house
                if qr.house:
                    qr.house.address = validated_data["address"]
                    qr.house.house_number = validated_data["house_number"]
                    qr.house.mahalla = mahalla
                    qr.house.owner = user
                    qr.house.save()
                    house = qr.house
                else:
                    house = House.objects.create(
                        address=validated_data["address"],
                        house_number=validated_data["house_number"],
                        mahalla=mahalla,
                        owner=user,
                    )
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
