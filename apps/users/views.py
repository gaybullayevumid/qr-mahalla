from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView

from .models import User, PhoneOTP, UserSession
from .serializers import AuthSerializer, UserListSerializer
from .services import send_sms


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


class AuthAPIView(APIView):
    """
    Combined authentication endpoint:
    - POST with phone only → send SMS code
    - POST with phone + code → verify and return token
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        code = serializer.validated_data.get("code")

        # Check if code is empty string or None
        if code:
            code = code.strip()

        # If no code provided → send SMS
        if not code:
            # Don't create user yet - only create after SMS verification
            # Just generate and send OTP

            # Invalidate old codes
            PhoneOTP.objects.filter(phone=phone, is_used=False).update(is_used=True)

            # Generate new code
            new_code = PhoneOTP.generate_code()
            PhoneOTP.objects.create(phone=phone, code=new_code)

            # Send SMS
            try:
                send_sms(phone, new_code)
                return Response(
                    {
                        "message": "SMS code sent",
                        "phone": phone,
                        "detail": "Please verify your phone number with the code sent via SMS",
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response(
                    {"error": "Error sending SMS"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # If code provided → verify and return token
        else:
            # Normalize phone number for comparison
            phone = phone.strip()
            code = code.strip()

            # Check OTP code first (before checking user)
            otp = (
                PhoneOTP.objects.filter(phone=phone, code=code, is_used=False)
                .order_by("-created_at")
                .first()
            )

            if not otp:
                # Debug: show what codes exist for this phone
                all_codes = PhoneOTP.objects.filter(phone=phone).order_by(
                    "-created_at"
                )[:3]
                debug_info = [
                    f"Code: {c.code}, Used: {c.is_used}, Created: {c.created_at}"
                    for c in all_codes
                ]
                return Response(
                    {
                        "error": "Code is incorrect or already used",
                        "debug": f"Looking for code '{code}' for phone '{phone}'",
                        "recent_codes": debug_info if settings.DEBUG else None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if otp.is_expired():
                return Response(
                    {"error": "Code has expired. Please request a new code"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Mark OTP as used
            otp.is_used = True
            otp.save()

            # Create user if doesn't exist (SMS kod tasdiqlangandan keyin)
            user, created = User.objects.get_or_create(
                phone=phone,
                defaults={
                    "is_verified": True,
                    "role": "user",
                },
            )

            # If user already exists, just verify them
            if not created:
                user.is_verified = True
                user.save()

            # Get device info from request
            device_id = request.data.get("device_id", "unknown")
            device_name = request.data.get("device_name", "")

            # Create JWT token
            refresh = RefreshToken.for_user(user)

            # Create or update session
            session, created = UserSession.objects.update_or_create(
                user=user,
                device_id=device_id,
                defaults={
                    "device_name": device_name,
                    "refresh_token": str(refresh),
                    "ip_address": get_client_ip(request),
                    "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                    "is_active": True,
                },
            )

            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": {
                        "phone": user.phone,
                        "role": user.role,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "scanned_qr_code": user.scanned_qr_code,
                        "has_scanned_qr": bool(user.scanned_qr_code),
                    },
                },
                status=status.HTTP_200_OK,
            )


class UserProfileAPIView(APIView):
    """
    Get user profile
    """

    permission_classes = [IsAuthenticated]
    schema = None

    def get(self, request):
        user = request.user

        if not user.is_authenticated or not hasattr(user, "role"):
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(
            {
                "phone": user.phone,
                "role": user.role,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "passport_id": user.passport_id,
                "address": user.address,
                "is_verified": user.is_verified,
                "scanned_qr_code": user.scanned_qr_code,
                "has_scanned_qr": bool(user.scanned_qr_code),
            }
        )


class UserSessionsAPIView(APIView):
    """
    Get user's active sessions
    """

    permission_classes = [IsAuthenticated]
    schema = None

    def get(self, request):
        sessions = UserSession.objects.filter(
            user=request.user, is_active=True
        ).order_by("-last_activity")

        session_list = []
        for session in sessions:
            session_list.append(
                {
                    "id": session.id,
                    "device_id": session.device_id,
                    "device_name": session.device_name,
                    "ip_address": session.ip_address,
                    "last_activity": session.last_activity,
                    "created_at": session.created_at,
                }
            )

        return Response({"count": len(session_list), "sessions": session_list})


class LogoutDeviceAPIView(APIView):
    """
    Logout from specific device
    """

    permission_classes = [IsAuthenticated]
    schema = None

    def post(self, request):
        device_id = request.data.get("device_id")

        if not device_id:
            return Response(
                {"error": "device_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            session = UserSession.objects.get(user=request.user, device_id=device_id)
            session.is_active = False
            session.save()

            return Response({"message": "Logged out successfully from this device"})
        except UserSession.DoesNotExist:
            return Response(
                {"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND
            )


class LogoutAllDevicesAPIView(APIView):
    """
    Logout from all devices except current
    """

    permission_classes = [IsAuthenticated]
    schema = None

    def post(self, request):
        current_device_id = request.data.get("device_id")

        # Deactivate all sessions except current device
        if current_device_id:
            UserSession.objects.filter(user=request.user, is_active=True).exclude(
                device_id=current_device_id
            ).update(is_active=False)
        else:
            # Deactivate all sessions
            UserSession.objects.filter(user=request.user, is_active=True).update(
                is_active=False
            )

        return Response({"message": "Logged out from all other devices"})


class UserRolesAPIView(APIView):
    """
    Get all available user roles
    Returns list of roles with value, label and permissions
    """

    permission_classes = [AllowAny]
    schema = None

    def get(self, request):
        roles = [
            {
                "value": "super_admin",
                "label": "Super Admin",
                "description": "Tizimning eng yuqori darajadagi administratori",
                "permissions": [
                    "Barcha CRUD operatsiyalar",
                    "Barcha regionlar, tumanlar, mahallalar",
                    "Barcha QR kodlar va uylar",
                    "Barcha userlarni boshqarish",
                    "QR kod delivery statuslarini o'zgartirish",
                ],
                "level": 5,
            },
            {
                "value": "government",
                "label": "Government Officer",
                "description": "Hukumat xodimi",
                "permissions": [
                    "Barcha regionlar, tumanlar, mahallalarni ko'rish va yaratish",
                    "Barcha QR kodlar va uylarni ko'rish",
                    "Ma'lumotlarni CREATE/UPDATE/DELETE",
                ],
                "level": 4,
            },
            {
                "value": "mahalla_admin",
                "label": "Neighborhood Admin",
                "description": "Mahalla administratori",
                "permissions": [
                    "Faqat o'z mahallasidagi ma'lumotlarni ko'rish",
                    "O'z mahallasida uylar yaratish",
                    "QR kodlarni delivery statusini belgilash",
                ],
                "level": 3,
            },
            {
                "value": "owner",
                "label": "House Owner",
                "description": "Uy egasi",
                "permissions": [
                    "O'z uyining ma'lumotlarini ko'rish",
                    "O'z uyining QR kodini ko'rish",
                    "Region/tuman/mahalla ma'lumotlarini ko'rish (GET only)",
                ],
                "level": 2,
            },
            {
                "value": "user",
                "label": "Regular User",
                "description": "Oddiy foydalanuvchi",
                "permissions": [
                    "QR kod skanerlash",
                    "House claim qilish (uy egasi bo'lish)",
                    "Region/tuman/mahalla ma'lumotlarini ko'rish (GET only)",
                ],
                "level": 1,
                "default": True,
            },
        ]

        return Response({"count": len(roles), "roles": roles})


class CustomTokenRefreshView(BaseTokenRefreshView):
    """Custom token refresh view hidden from Swagger"""

    schema = None


class UserViewSet(ReadOnlyModelViewSet):
    """Read-only viewset for listing and retrieving users with their houses"""

    queryset = User.objects.prefetch_related("houses__mahalla__district__region").all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]
