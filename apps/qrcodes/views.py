from typing import Dict, Any, Optional
import os
import zipfile
from io import BytesIO

from django.db import transaction, IntegrityError
from django.db.models import Q, Max
from django.http import HttpResponse, FileResponse
from django.conf import settings

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
    BulkQRCodeGenerateSerializer,
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
    Mark QR code as scanned.

    Args:
        request: HTTP request object
        qr: QRCode object being scanned
    """
    # Mark QR as scanned
    if not qr.is_scanned:
        qr.is_scanned = True
        qr.save(update_fields=["is_scanned"])

    if request.user and request.user.is_authenticated:
        ScanLog.objects.create(
            qr=qr, scanned_by=request.user, ip_address=get_client_ip(request)
        )
        request.user.scanned_qr_code = qr.uuid
        request.user.save(update_fields=["scanned_qr_code"])

        # QR kod skanerlanganda SMS yuborish
        try:
            from apps.users.services import send_qr_scan_sms

            send_qr_scan_sms(request.user.phone, qr.uuid)
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(f"QR kod skaner SMS yuborishda xatolik: {e}")


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
    GET/POST endpoint for QR code scanning by UUID.

    Main endpoint for all users to scan QR codes.

    GET: Scan QR code and get status
    POST: Scan QR code with user data (saves user info)
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

    def post(self, request: Request, uuid: str) -> Response:
        """
        Handle QR code scan via POST request with user data.

        Accepts user info in request body and saves it:
        {
            "first_name": "John",
            "last_name": "Doe"
        }
        """
        try:
            qr = QRCode.objects.select_related(
                "house__owner",
                "house__mahalla__district__region",
            ).get(uuid=uuid)
        except QRCode.DoesNotExist:
            return Response(
                {"error": "QR code not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Save user data if authenticated
        if request.user and request.user.is_authenticated:
            # Update user info from request body
            first_name = request.data.get("first_name")
            last_name = request.data.get("last_name")

            if first_name or last_name:
                if first_name:
                    request.user.first_name = first_name
                if last_name:
                    request.user.last_name = last_name

                # Save scanned QR UUID
                request.user.scanned_qr_code = qr.uuid
                request.user.save(
                    update_fields=["first_name", "last_name", "scanned_qr_code"]
                )

        # Log the scan
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

        logger.info("Claim start: Using random House IDs with retry logic")

        # CRITICAL: Cleanup orphaned house_ids BEFORE any transaction attempts
        # This prevents UNIQUE constraint errors from orphaned references
        logger.info("Pre-claim cleanup: checking for orphaned house_ids globally")

        try:
            existing_house_ids = set(House.objects.values_list("id", flat=True))
            used_house_ids_in_qr = set(
                QRCode.objects.filter(house_id__isnull=False).values_list(
                    "house_id", flat=True
                )
            )
            orphaned_ids = used_house_ids_in_qr - existing_house_ids

            if orphaned_ids:
                logger.warning(
                    f"Found {len(orphaned_ids)} orphaned house_ids: {sorted(list(orphaned_ids))[:20]}..."
                )
                cleaned = QRCode.objects.filter(house_id__in=orphaned_ids).update(
                    house_id=None
                )
                logger.info(f"Successfully cleaned up {cleaned} orphaned house_ids")
            else:
                logger.info("No orphaned house_ids found. Database is clean.")
        except Exception as e:
            logger.error(f"Error during orphaned house_ids cleanup: {str(e)}")
            # Continue anyway, retry logic will handle conflicts

        # Retry logic OUTSIDE transaction to avoid "can't execute queries" error
        import random

        max_attempts = 50
        last_error = None

        for attempt in range(max_attempts):
            try:
                with transaction.atomic():
                    logger.info(f"Claim attempt {attempt + 1}/{max_attempts}")

                    # Lock ONLY the QR code row (no JOINs to avoid PostgreSQL FOR UPDATE error)
                    # select_for_update() cannot be used with nullable outer joins
                    qr = QRCode.objects.select_for_update().get(uuid=uuid)

                    # Access related objects AFTER lock is acquired (separate queries)
                    # This avoids "FOR UPDATE cannot be applied to nullable side of outer join" error
                    house = qr.house  # Triggers separate query if needed
                    owner = (
                        house.owner if house else None
                    )  # Triggers separate query if needed

                    logger.info(
                        f"QR {uuid} - has_house={house is not None}, "
                        f"has_owner={owner}"
                    )

                    # Check if already claimed
                    if house and owner:
                        if owner == user:
                            return Response(
                                {
                                    "error": "Siz allaqachon bu uyni claim qilgansiz.",
                                    "error_en": "You have already claimed this house.",
                                    "house_id": house.id,
                                    "is_reclaim_attempt": True,
                                },
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                        return Response(
                            {
                                "error": "Bu uy allaqachon boshqa foydalanuvchi tomonidan claim qilingan.",
                                "error_en": "This house is already claimed by another user.",
                                "owner": owner.phone,
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    # Update user info with QR code reference
                    user.first_name = validated_data["first_name"]
                    user.last_name = validated_data["last_name"]
                    user.scanned_qr_code = qr.uuid  # Save scanned QR UUID
                    user.save(
                        update_fields=["first_name", "last_name", "scanned_qr_code"]
                    )

                    logger.info(
                        f"Updated user {user.phone}: {user.first_name} {user.last_name}, "
                        f"scanned QR: {user.scanned_qr_code}"
                    )

                    if house:
                        # Update existing house
                        logger.info(f"Updating existing house {house.id}")
                        house.address = validated_data["address"]
                        house.house_number = validated_data["house_number"]
                        house.mahalla = mahalla
                        house.owner = user
                        house.save()
                    else:
                        # Create new house with random 10-digit ID
                        # Orphaned house_ids already cleaned up before transaction
                        logger.info("Generating random House ID")

                        random_id = random.randint(1_000_000_000, 9_999_999_999)
                        logger.info(f"Selected House ID: {random_id}")

                        # Create house with random ID
                        house = House(
                            id=random_id,
                            address=validated_data["address"],
                            house_number=validated_data["house_number"],
                            mahalla=mahalla,
                            owner=user,
                        )
                        house.save(force_insert=True)
                        logger.info(f"Successfully created house with ID {house.id}")

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

                    # Send SMS to user after successful house claim
                    try:
                        from apps.users.services import EskizSMSService

                        sms_service = EskizSMSService()
                        message = "Siz QR MAHALLA tizimida muvaffaqiyatli ro'yxatdan o'tdingiz."
                        sms_service.send_sms(user.phone, message)
                        logger.info(f"SMS sent to {user.phone} after house claim")
                    except Exception as e:
                        logger.warning(f"Failed to send SMS after house claim: {e}")

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
                logger.warning(f"Attempt {attempt + 1} failed: {error_msg}")

                # If UNIQUE constraint on house_id, retry with different ID
                if (
                    "unique constraint" in error_msg.lower()
                    and "house_id" in error_msg.lower()
                ):
                    if attempt < max_attempts - 1:
                        logger.info(f"Will retry with new random ID...")
                        continue

                # For other IntegrityErrors, stop retrying
                break
            except QRCode.DoesNotExist:
                return Response(
                    {"error": "QR code not found"}, status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                # Unexpected error, log and retry if possible
                logger.error(f"Unexpected error in attempt {attempt + 1}: {str(e)}")
                last_error = e
                if attempt < max_attempts - 1:
                    continue
                break

        # If we get here, all retries failed
        if last_error:
            logger.error(f"Failed after {max_attempts} attempts")
            error_msg = str(last_error)

            if isinstance(last_error, IntegrityError):
                if (
                    "unique constraint" in error_msg.lower()
                    or "duplicate" in error_msg.lower()
                ):
                    return Response(
                        {
                            "error": "Bu uy allaqachon boshqa QR kod bilan bog'langan.",
                            "error_en": "This house is already linked to another QR code.",
                            "detail": error_msg,
                            "error_type": "house_already_linked",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                return Response(
                    {
                        "error": "Ma'lumotlar bazasida xatolik yuz berdi.",
                        "error_en": "Database integrity error occurred.",
                        "detail": error_msg,
                        "error_type": "integrity_error",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "error": "Uyni claim qilishda kutilmagan xatolik yuz berdi.",
                    "error_en": "An unexpected error occurred while claiming the house.",
                    "detail": error_msg,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Should never reach here
        return Response(
            {
                "error": "Uyni claim qilishda kutilmagan xatolik yuz berdi.",
                "error_en": "An unexpected error occurred while claiming the house.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class BulkQRCodeGenerateView(APIView):
    """
    Bulk QR code generation endpoint.

    Generates multiple QR codes, creates a zip file, and returns download link.
    Requires authentication and admin permissions.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Generate multiple QR codes and return zip file.

        Expected payload:
        {
            "count": 10  // Number of QR codes to generate
        }

        Returns:
        {
            "download_url": "/media/qr_downloads/qrcodes_123.zip",
            "count": 10,
            "message": "QR codes generated successfully"
        }
        """
        # Check admin permissions
        user_role = getattr(request.user, "role", None)
        if user_role not in ADMIN_ROLES:
            return Response(
                {
                    "error": "Ruxsat yo'q. Faqat admin foydalanuvchilar QR kod yaratishi mumkin.",
                    "error_en": "Permission denied. Only admin users can generate QR codes.",
                    "error_type": "permission_denied",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = BulkQRCodeGenerateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        count = serializer.validated_data["count"]

        try:
            # Generate QR codes
            qr_codes = []
            with transaction.atomic():
                for _ in range(count):
                    qr_code = QRCode.objects.create()
                    qr_codes.append(qr_code)

            # Create zip file in memory
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for qr in qr_codes:
                    if qr.image:
                        # Add QR code image to zip
                        img_name = f"qr_{qr.uuid}.png"
                        zip_file.writestr(img_name, qr.image.read())

            # Save zip file to media folder
            zip_buffer.seek(0)
            zip_filename = (
                f"qrcodes_{request.user.id}_{QRCode.objects.latest('id').id}.zip"
            )
            zip_path = os.path.join(settings.MEDIA_ROOT, "qr_downloads", zip_filename)

            # Create directory if not exists
            os.makedirs(os.path.dirname(zip_path), exist_ok=True)

            # Write zip file
            with open(zip_path, "wb") as f:
                f.write(zip_buffer.getvalue())

            # Generate absolute download URL (with domain)
            download_url = request.build_absolute_uri(
                f"/media/qr_downloads/{zip_filename}"
            )

            return Response(
                {
                    "download_url": download_url,
                    "count": count,
                    "filename": zip_filename,
                    "message": "QR kodlar muvaffaqiyatli yaratildi",
                    "message_en": "QR codes generated successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {
                    "error": "QR kod yaratishda xatolik yuz berdi.",
                    "error_en": "Error occurred while generating QR codes.",
                    "detail": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class QRCodeBulkListView(generics.ListAPIView):
    """
    List recently created QR codes.

    Returns paginated list of QR codes with optional filtering.
    """

    serializer_class = QRCodeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get QR codes based on user role."""
        user_role = getattr(self.request.user, "role", None)

        # Only admin users can view all QR codes
        if user_role not in ADMIN_ROLES:
            return QRCode.objects.none()

        queryset = QRCode.objects.all().order_by("-created_at")

        # Optional filtering by claimed status
        is_claimed = self.request.query_params.get("is_claimed")
        if is_claimed is not None:
            if is_claimed.lower() == "true":
                queryset = queryset.filter(house__owner__isnull=False)
            elif is_claimed.lower() == "false":
                queryset = queryset.filter(
                    Q(house__isnull=True) | Q(house__owner__isnull=True)
                )

        # Limit to recent QR codes (optional limit parameter)
        limit = self.request.query_params.get("limit")
        if limit:
            try:
                queryset = queryset[: int(limit)]
            except ValueError:
                pass

        return queryset


class BulkQRCodeDownloadView(APIView):
    """
    Direct download endpoint for generated ZIP files.

    Alternative to using media URL - provides direct file download.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, filename):
        """
        Download ZIP file directly.

        URL: /api/qrcodes/bulk/download/{filename}/
        """
        # Check admin permissions
        user_role = getattr(request.user, "role", None)
        if user_role not in ADMIN_ROLES:
            return Response(
                {
                    "error": "Ruxsat yo'q.",
                    "error_en": "Permission denied.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Security: Validate filename (prevent directory traversal)
        if ".." in filename or "/" in filename or "\\" in filename:
            return Response(
                {
                    "error": "Noto'g'ri fayl nomi.",
                    "error_en": "Invalid filename.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Build file path
        zip_path = os.path.join(settings.MEDIA_ROOT, "qr_downloads", filename)

        # Check if file exists
        if not os.path.exists(zip_path):
            return Response(
                {
                    "error": "Fayl topilmadi.",
                    "error_en": "File not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Return file as download
        try:
            response = FileResponse(
                open(zip_path, "rb"), content_type="application/zip"
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            return Response(
                {
                    "error": "Faylni yuklab olishda xatolik.",
                    "error_en": "Error downloading file.",
                    "detail": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
