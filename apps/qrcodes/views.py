from typing import Dict, Any, Optional

from django.db import transaction, IntegrityError
from django.db.models import Q, Max

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
    data = {
        "id": owner.id,
        "first_name": owner.first_name,
        "last_name": owner.last_name,
        "phone": owner.phone,
    }

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
        Response data dictionary with status, message, QR info, house info, and claim options
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

        if "t.me/" in data or "telegram.me/" in data:
            if "QR_KEY_" in data:
                parts = data.split("QR_KEY_")
                if len(parts) > 1:
                    return parts[1].strip()

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

        uuid = self.extract_uuid(raw_data)

        if not uuid:
            return Response(
                {"error": "Invalid QR code format"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            qr = QRCode.objects.select_related(
                "house__owner",
                "house__mahalla__district__region",
            ).get(uuid=uuid)
        except QRCode.DoesNotExist:
            return Response(
                {"error": "QR code not found"}, status=status.HTTP_404_NOT_FOUND
            )

        _log_qr_scan(request, qr)
        user_role, is_owner = _get_user_role_and_ownership(request, qr)

        if not qr.house or not qr.house.owner:
            return Response(_get_unclaimed_response(qr, user_role))

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

        _log_qr_scan(request, qr)

        user_role, is_owner = _get_user_role_and_ownership(request, qr)

        if not qr.house or not qr.house.owner:
            return Response(_get_unclaimed_response(qr, user_role))

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

        if role == CLIENT_ROLE:
            return queryset.filter(Q(house__isnull=True) | Q(house__owner__isnull=True))

        if role == LEADER_ROLE and hasattr(user, "mahalla"):
            return queryset.filter(house__mahalla=user.mahalla)

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

        if role == CLIENT_ROLE:
            return queryset.filter(
                Q(house__isnull=True)
                | Q(house__owner__isnull=True)
                | Q(house__owner=user)
            )

        if role == LEADER_ROLE and hasattr(user, "mahalla"):
            return queryset.filter(house__mahalla=user.mahalla)

        return queryset


class ClaimHouseView(APIView):
    """
    Claim house ownership after scanning QR code.

    GET: Get claim status and debug info for a QR code
    POST: Claim house ownership

    Only authenticated users can claim houses.
    Uses atomic transactions to prevent race conditions.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, uuid: str) -> Response:
        """
        Get claim status and debug info for a QR code.

        Returns QR code details, house info, and whether it can be claimed.
        """
        try:
            qr = QRCode.objects.select_related(
                "house", "house__owner", "house__mahalla"
            ).get(uuid=uuid)

            response_data = {
                "qr_uuid": qr.uuid,
                "qr_id": qr.id,
                "has_house": qr.house is not None,
                "is_claimed": bool(qr.house and qr.house.owner is not None),
                "can_claim": not (qr.house and qr.house.owner),
            }

            if qr.house:
                response_data["house"] = {
                    "id": qr.house.id,
                    "address": qr.house.address,
                    "house_number": qr.house.house_number,
                    "mahalla_id": qr.house.mahalla.id,
                    "mahalla_name": qr.house.mahalla.name,
                    "has_owner": qr.house.owner is not None,
                }
                if qr.house.owner:
                    response_data["house"]["owner"] = {
                        "id": qr.house.owner.id,
                        "phone": qr.house.owner.phone,
                        "first_name": qr.house.owner.first_name,
                        "last_name": qr.house.owner.last_name,
                    }
                    response_data["message"] = "Bu uy allaqachon claim qilingan."
                else:
                    response_data["message"] = "Bu uyni claim qilishingiz mumkin."
            else:
                response_data["message"] = (
                    "Bu QR kod uchun uy ma'lumotlari kiritilmagan."
                )

            return Response(response_data)
        except QRCode.DoesNotExist:
            return Response(
                {"error": "QR code not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request: Request, uuid: str) -> Response:
        """Handle house claim request."""
        # Log incoming request for debugging
        import logging

        logger = logging.getLogger(__name__)
        logger.info(
            f"Claim request for QR {uuid} from user {request.user.phone if request.user else 'anonymous'}"
        )

        serializer = QRCodeClaimSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        validated_data = serializer.validated_data

        logger.info(f"Claim data: {validated_data}")

        try:
            mahalla = Mahalla.objects.get(id=validated_data["mahalla"])
        except Mahalla.DoesNotExist:
            return Response(
                {"error": "Mahalla not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Retry logic for handling GapFillingIDMixin conflicts
        max_retries = 20
        last_error = None

        from django.db.models import Max
        from apps.qrcodes.models import QRCode as QRCodeModel

        for attempt in range(max_retries):
            try:
                with transaction.atomic():
                    # Lock QRCode and House tables to prevent race conditions
                    # This ensures only one transaction can get max ID at a time
                    QRCodeModel.objects.select_for_update().exists()
                    House.objects.select_for_update().exists()

                    # Now safely get max IDs within locked transaction
                    max_house_id = House.objects.aggregate(Max("id"))["id__max"] or 0
                    max_qr_house_id = (
                        QRCodeModel.objects.filter(house_id__isnull=False).aggregate(
                            Max("house_id")
                        )["house_id__max"]
                        or 0
                    )

                    # Start with max + 1, then add attempt number for retries
                    next_house_id = max(max_house_id, max_qr_house_id) + 1 + attempt

                    logger.info(
                        f"Attempt {attempt + 1}: Will use house ID {next_house_id} "
                        f"(max_house={max_house_id}, max_qr={max_qr_house_id}, attempt={attempt})"
                    )
                    # Lock the QR code row to prevent race conditions
                    qr = (
                        QRCode.objects.select_for_update()
                        .select_related("house", "house__owner")
                        .get(uuid=uuid)
                    )

                    logger.info(
                        f"Attempt {attempt + 1}: QR {uuid} - has_house={qr.house is not None}, has_owner={qr.house.owner if qr.house else None}"
                    )

                    # Check if already claimed
                    if qr.house and qr.house.owner:
                        if qr.house.owner == user:
                            return Response(
                                {
                                    "error": "Siz allaqachon bu uyni claim qilgansiz.",
                                    "error_en": "You have already claimed this house.",
                                    "house_id": qr.house.id,
                                    "is_reclaim_attempt": True,
                                },
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                        return Response(
                            {
                                "error": "Bu uy allaqachon boshqa foydalanuvchi tomonidan claim qilingan.",
                                "error_en": "This house is already claimed by another user.",
                                "owner": qr.house.owner.phone,
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    # Update user info
                    user.first_name = validated_data["first_name"]
                    user.last_name = validated_data["last_name"]
                    user.save(update_fields=["first_name", "last_name"])

                    if qr.house:
                        # Update existing house
                        logger.info(f"Updating existing house {qr.house.id}")
                        qr.house.address = validated_data["address"]
                        qr.house.house_number = validated_data["house_number"]
                        qr.house.mahalla = mahalla
                        qr.house.owner = user
                        qr.house.save()
                        house = qr.house
                    else:
                        # Create new house with safe ID
                        # For first attempt, use max+1
                        # For retries, add attempt number to avoid conflicts
                        logger.info(
                            f"Creating new house (attempt {attempt + 1}) with ID {next_house_id}"
                        )

                        # IMPORTANT: Explicitly set ID to override GapFillingIDMixin
                        # which might choose an ID that's already linked to a QRCode
                        house = House(
                            id=next_house_id,
                            address=validated_data["address"],
                            house_number=validated_data["house_number"],
                            mahalla=mahalla,
                            owner=user,
                        )

                        # Save with force_insert to ensure ID is respected
                        house.save(force_insert=True)
                        logger.info(f"Created house with ID {house.id}")

                        # Link QR to house
                        qr.house = house
                        qr.save(update_fields=["house"])
                        logger.info(
                            f"Successfully linked QR {qr.uuid} to house {house.id}"
                        )

                    # Log the scan
                    ScanLog.objects.create(
                        qr=qr, scanned_by=user, ip_address=get_client_ip(request)
                    )

                    # Success! Return response
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
                                "is_claimed": True,
                            },
                        }
                    )

            except IntegrityError as ie:
                last_error = ie
                error_msg = str(ie)
            except IntegrityError as ie:
                last_error = ie
                error_msg = str(ie)
                logger.warning(
                    f"Attempt {attempt + 1} failed with ID {next_house_id}: {error_msg}"
                )

                # If house_id constraint error, retry with next ID
                if (
                    "house_id" in error_msg.lower()
                    or "qrcodes_qrcode.house_id" in error_msg
                ):
                    if attempt < max_retries - 1:
                        logger.info(f"Will retry with ID {next_house_id + 1}")
                        continue

                # For other errors, stop retrying
                break

        # If we exhausted all retries, return error
        if last_error:
            logger.error(f"Failed to claim house after {max_retries} attempts")
            error_msg = str(last_error).lower()
            error_detail = str(last_error)

            if "unique constraint" in error_msg or "duplicate" in error_msg:
                if (
                    "house" in error_msg
                    or "qr_code" in error_msg
                    or "one-to-one" in error_msg
                ):
                    return Response(
                        {
                            "error": f"Bu uy allaqachon boshqa QR kod bilan bog'langan. ({error_detail})",
                            "error_en": f"This house is already linked to another QR code. ({error_detail})",
                            "detail": error_detail,
                            "error_type": "house_already_linked",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            return Response(
                {
                    "error": f"Ma'lumotlar bazasida xatolik yuz berdi: {error_detail}",
                    "error_en": f"Database integrity error: {error_detail}",
                    "detail": error_detail,
                    "error_type": "integrity_error",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # If no error but also no success (shouldn't happen)
        return Response(
            {
                "error": "Uyni claim qilishda kutilmagan xatolik yuz berdi.",
                "error_en": "An unexpected error occurred while claiming the house.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
