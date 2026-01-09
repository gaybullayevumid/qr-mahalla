from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
import logging

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView

from .models import User, PhoneOTP, UserSession
from .serializers import (
    AuthSerializer,
    UserListSerializer,
    UserCreateUpdateSerializer,
    UserMinimalSerializer,
)
from .services import send_sms, send_registration_success_sms
from .sms_utils import (
    send_verification_code,
    verify_code,
    notify_new_user_registered,
)

logger = logging.getLogger(__name__)


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

        if code:
            code = code.strip()

        if not code:
            # Tasdiqlash kodini yuborish (yangi utility funksiya ishlatish)
            result = send_verification_code(phone)

            if result["success"]:
                return Response(
                    {
                        "message": "SMS code sent",
                        "phone": phone,
                        "detail": "Please verify your phone number with the code sent via SMS",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": result["message"]},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        else:
            # Kodni tekshirish (yangi utility funksiya ishlatish)
            verification_result = verify_code(phone, code)

            if not verification_result["valid"]:
                return Response(
                    {"error": verification_result["message"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Kod to'g'ri - user yaratish yoki topish
            user, created = User.objects.get_or_create(
                phone=phone,
                defaults={
                    "is_verified": True,
                    "role": "client",
                },
            )

            if not created:
                user.is_verified = True
                user.save()
            else:
                # Yangi foydalanuvchi ro'yxatdan o'tganda SMS yuborish
                notify_new_user_registered(phone)

            device_id = request.data.get("device_id", "unknown")
            device_name = request.data.get("device_name", "")

            refresh = RefreshToken.for_user(user)
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

            available_roles = [
                {
                    "value": "admin",
                    "label": "Admin",
                    "level": 4,
                },
                {
                    "value": "gov",
                    "label": "Government",
                    "level": 3,
                },
                {
                    "value": "leader",
                    "label": "Leader",
                    "level": 2,
                },
                {
                    "value": "client",
                    "label": "Client",
                    "level": 1,
                },
                {
                    "value": "agent",
                    "label": "Agent",
                    "level": 1,
                },
            ]

            from apps.houses.models import House
            from apps.qrcodes.models import QRCode

            houses = House.objects.filter(owner=user).select_related(
                "mahalla__district__region"
            )

            house_list = []
            for house in houses:
                # Get first QR code for this house (ForeignKey allows multiple)
                qr_code = house.qr_codes.first()
                scanned_qr = qr_code.uuid if qr_code else None

                house_list.append(
                    {
                        "id": house.id,
                        "address": house.address,
                        "house_number": house.house_number,
                        "mahalla": house.mahalla.name,
                        "district": house.mahalla.district.name,
                        "region": house.mahalla.district.region.name,
                        "scanned_qr_code": scanned_qr,
                    }
                )

            user_role_obj = next(
                (r for r in available_roles if r["value"] == user.role),
                {
                    "value": user.role,
                    "label": user.role.replace("_", " ").title(),
                    "level": 0,
                },
            )

            response_data = {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "phone": user.phone,
                    "role": user_role_obj,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_verified": user.is_verified,
                    "houses": house_list,
                },
                "available_roles": available_roles,
            }

            return Response(response_data, status=status.HTTP_200_OK)


class UserProfileAPIView(APIView):
    """
    API endpoint for retrieving and updating user profile information.

    Provides GET, PUT, PATCH, and POST methods for profile management.
    Requires authentication.
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

        from apps.houses.models import House
        from apps.qrcodes.models import QRCode

        houses = House.objects.filter(owner=user).select_related(
            "mahalla__district__region"
        )

        house_list = []
        for house in houses:
            # Get first QR code for this house (ForeignKey allows multiple)
            qr_code = house.qr_codes.first()
            scanned_qr = qr_code.uuid if qr_code else None

            house_list.append(
                {
                    "id": house.id,
                    "address": house.address,
                    "house_number": house.house_number,
                    "mahalla": house.mahalla.name,
                    "district": house.mahalla.district.name,
                    "region": house.mahalla.district.region.name,
                    "scanned_qr_code": scanned_qr,
                }
            )

        response_data = {
            "id": user.id,
            "phone": user.phone,
            "role": user.role,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_verified": user.is_verified,
            "scanned_qr_code": user.scanned_qr_code,  # Include scanned QR code
            "houses": house_list,
        }

        return Response(response_data)

    def put(self, request):
        """Update user profile with allowed fields."""
        user = request.user
        allowed_fields = ["first_name", "last_name"]

        for field in allowed_fields:
            if field in request.data:
                setattr(user, field, request.data[field])

        user.save()

        return self.get(request)

    def patch(self, request):
        """Partial update of user profile."""
        return self.put(request)

    def post(self, request):
        """Handle POST requests by redirecting to PUT method."""
        return self.put(request)


class UserSessionsAPIView(APIView):
    """
    API endpoint for retrieving user's active sessions across all devices.
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
    API endpoint for logging out from a specific device session.
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
    API endpoint for logging out from all devices except the current one.
    """

    permission_classes = [IsAuthenticated]
    schema = None

    def post(self, request):
        current_device_id = request.data.get("device_id")

        if current_device_id:
            UserSession.objects.filter(user=request.user, is_active=True).exclude(
                device_id=current_device_id
            ).update(is_active=False)
        else:
            UserSession.objects.filter(user=request.user, is_active=True).update(
                is_active=False
            )

        return Response({"message": "Logged out from all other devices"})


class UserRolesAPIView(APIView):
    """
    API endpoint for retrieving all available user roles.

    Returns a list of roles with their values, labels, descriptions,
    permissions, and hierarchy levels.
    """

    permission_classes = [AllowAny]
    schema = None

    def get(self, request):
        roles = [
            {
                "value": "admin",
                "label": "Admin",
                "description": "Tizimning eng yuqori darajadagi administratori",
                "permissions": [
                    "Barcha CRUD operatsiyalar",
                    "Barcha regionlar, tumanlar, mahallalar",
                    "Barcha QR kodlar va uylar",
                    "Barcha userlarni boshqarish",
                ],
                "level": 4,
            },
            {
                "value": "gov",
                "label": "Government",
                "description": "Hukumat xodimi",
                "permissions": [
                    "Barcha regionlar, tumanlar, mahallalarni ko'rish va yaratish",
                    "Barcha QR kodlar va uylarni ko'rish",
                    "Ma'lumotlarni CREATE/UPDATE/DELETE",
                ],
                "level": 3,
            },
            {
                "value": "leader",
                "label": "Leader",
                "description": "Mahalla administratori",
                "permissions": [
                    "Faqat o'z mahallasidagi ma'lumotlarni ko'rish",
                    "O'z mahallasida uylar yaratish",
                ],
                "level": 2,
            },
            {
                "value": "client",
                "label": "Client",
                "description": "Oddiy foydalanuvchi va uy egasi",
                "permissions": [
                    "QR kod skanerlash",
                    "House claim qilish (uy egasi bo'lish)",
                    "O'z uyining ma'lumotlarini ko'rish",
                    "Region/tuman/mahalla ma'lumotlarini ko'rish (GET only)",
                ],
                "level": 1,
                "default": True,
            },
            {
                "value": "agent",
                "label": "Agent",
                "description": "Agent foydalanuvchi",
                "permissions": [
                    "QR kod skanerlash",
                    "Ma'lumotlarni ko'rish",
                ],
                "level": 1,
            },
        ]

        return Response({"count": len(roles), "roles": roles})


class CustomTokenRefreshView(BaseTokenRefreshView):
    """Custom token refresh view excluded from API documentation."""

    schema = None


class UserViewSet(ModelViewSet):
    """
    CRUD viewset for managing users and their associated houses.

    Implements role-based access control where different user roles
    have different levels of access to user data.
    """

    queryset = User.objects.prefetch_related("houses__mahalla__district__region").all()
    permission_classes = [AllowAny]  # Temporarily allow any

    def get_serializer_class(self):
        """Return appropriate serializer class based on the action being performed."""
        if self.action in ["create", "update", "partial_update"]:
            return UserCreateUpdateSerializer
        return UserListSerializer

    def get_serializer_context(self):
        """Add request to serializer context for role-based data filtering."""
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        """
        Filter users based on the requesting user's role.

        - Clients: see only themselves
        - Leaders: see users in their mahalla
        - Admin/Government: see all users
        """
        user = self.request.user
        role = getattr(user, "role", None)

        if not role:
            return User.objects.none()

        if role == "client":
            return User.objects.filter(id=user.id).prefetch_related(
                "houses__mahalla__district__region"
            )

        if role == "leader" and hasattr(user, "mahalla"):
            return (
                User.objects.filter(houses__mahalla=user.mahalla)
                .distinct()
                .prefetch_related("houses__mahalla__district__region")
            )
        return User.objects.all().prefetch_related("houses__mahalla__district__region")

    def get_permissions(self):
        """
        Determine permissions based on the action being performed.

        All actions require authentication. Data access is further
        filtered by role in other methods.
        """
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]

        if self.action in ["update", "partial_update"]:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        """
        Update user instance with permission validation.

        Regular clients can only update their own profile.
        """
        instance = self.get_object()
        user = request.user

        if user.role == "client" and instance.id != user.id:
            return Response(
                {"error": "You can only update your own profile"},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update user instance with permission validation.

        Regular clients can only update their own profile.
        """
        instance = self.get_object()
        user = request.user

        if user.role == "client" and instance.id != user.id:
            return Response(
                {"error": "You can only update your own profile"},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().partial_update(request, *args, **kwargs)


class SMSLogViewSet(ModelViewSet):
    """
    SMS log view set.
    Admin va gov foydalanuvchilari barcha SMS loglarni ko'rishi mumkin.
    """

    from .models_sms import SMSLog
    from .serializers_sms import SMSLogSerializer

    queryset = SMSLog.objects.all()
    serializer_class = SMSLogSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "head", "options"]  # Faqat o'qish uchun

    def get_queryset(self):
        """Filter SMS logs based on user role."""
        # Swagger uchun
        if getattr(self, "swagger_fake_view", False):
            return self.queryset.none()

        user = self.request.user
        role = getattr(user, "role", None)

        # Admin va gov barcha loglarni ko'radi
        if role in ["admin", "gov"]:
            return self.queryset.select_related("user")

        # Boshqa foydalanuvchilar faqat o'z loglarini ko'radi
        return self.queryset.filter(phone=user.phone).select_related("user")


class SMSStatisticsAPIView(APIView):
    """
    SMS statistikasi API.
    Faqat admin va gov foydalanuvchilari uchun.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get SMS statistics"""
        user = request.user
        role = getattr(user, "role", None)

        # Faqat admin va gov ko'rishi mumkin
        if role not in ["admin", "gov"]:
            return Response(
                {"error": "Sizda bu ma'lumotni ko'rish huquqi yo'q"},
                status=status.HTTP_403_FORBIDDEN,
            )

        from .models_sms import SMSLog
        from django.db.models import Count, Q

        # Umumiy statistika
        total_sms = SMSLog.objects.count()
        sent_sms = SMSLog.objects.filter(status="sent").count()
        failed_sms = SMSLog.objects.filter(status="failed").count()
        pending_sms = SMSLog.objects.filter(status="pending").count()

        # SMS turlari bo'yicha
        verification_sms = SMSLog.objects.filter(sms_type="verification").count()
        registration_sms = SMSLog.objects.filter(sms_type="registration").count()
        qr_scan_sms = SMSLog.objects.filter(sms_type="qr_scan").count()
        notification_sms = SMSLog.objects.filter(sms_type="notification").count()

        # Success rate
        success_rate = (sent_sms / total_sms * 100) if total_sms > 0 else 0

        data = {
            "total_sms": total_sms,
            "sent_sms": sent_sms,
            "failed_sms": failed_sms,
            "pending_sms": pending_sms,
            "verification_sms": verification_sms,
            "registration_sms": registration_sms,
            "qr_scan_sms": qr_scan_sms,
            "notification_sms": notification_sms,
            "success_rate": round(success_rate, 2),
        }

        from .serializers_sms import SMSStatisticsSerializer

        serializer = SMSStatisticsSerializer(data)
        return Response(serializer.data)
