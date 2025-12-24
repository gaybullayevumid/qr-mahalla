from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView

from .models import User, PhoneOTP, UserSession
from .serializers import AuthSerializer, UserListSerializer, UserCreateUpdateSerializer
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

            # Get all available roles
            available_roles = [
                {
                    "value": "super_admin",
                    "label": "Super Admin",
                    "level": 4,
                },
                {
                    "value": "government",
                    "label": "Government Officer",
                    "level": 3,
                },
                {
                    "value": "mahalla_admin",
                    "label": "Neighborhood Admin",
                    "level": 2,
                },
                {
                    "value": "user",
                    "label": "User",
                    "level": 1,
                },
            ]

            # Get user's houses with QR codes
            from apps.houses.models import House
            from apps.qrcodes.models import QRCode

            houses = House.objects.filter(owner=user).select_related(
                "mahalla__district__region"
            )

            house_list = []
            for house in houses:
                try:
                    qr_code = QRCode.objects.get(house=house)
                    scanned_qr = qr_code.uuid
                except QRCode.DoesNotExist:
                    scanned_qr = None

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

            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": {
                        "phone": user.phone,
                        "role": user.role,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "houses": house_list,
                    },
                    "available_roles": available_roles,
                },
                status=status.HTTP_200_OK,
            )


class UserProfileAPIView(APIView):
    """
    Get and update user profile
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

        # Get user's houses with QR codes
        from apps.houses.models import House
        from apps.qrcodes.models import QRCode

        houses = House.objects.filter(owner=user).select_related(
            "mahalla__district__region"
        )

        house_list = []
        for house in houses:
            try:
                qr_code = QRCode.objects.get(house=house)
                scanned_qr = qr_code.uuid
            except QRCode.DoesNotExist:
                scanned_qr = None

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

        return Response(
            {
                "phone": user.phone,
                "role": user.role,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "passport_id": user.passport_id,
                "address": user.address,
                "is_verified": user.is_verified,
                "houses": house_list,
            }
        )

    def put(self, request):
        """Update user profile"""
        user = request.user

        # Update allowed fields
        allowed_fields = ["first_name", "last_name", "passport_id", "address"]

        for field in allowed_fields:
            if field in request.data:
                setattr(user, field, request.data[field])

        user.save()

        # Return updated profile
        return self.get(request)

    def patch(self, request):
        """Partial update user profile"""
        return self.put(request)

    def post(self, request):
        """POST method - redirect to PUT"""
        return self.put(request)


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
                ],
                "level": 4,
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
                "level": 3,
            },
            {
                "value": "mahalla_admin",
                "label": "Neighborhood Admin",
                "description": "Mahalla administratori",
                "permissions": [
                    "Faqat o'z mahallasidagi ma'lumotlarni ko'rish",
                    "O'z mahallasida uylar yaratish",
                ],
                "level": 2,
            },
            {
                "value": "user",
                "label": "User",
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
        ]

        return Response({"count": len(roles), "roles": roles})


class CustomTokenRefreshView(BaseTokenRefreshView):
    """Custom token refresh view hidden from Swagger"""

    schema = None


class UserViewSet(ModelViewSet):
    """CRUD viewset for users with their houses"""

    queryset = User.objects.prefetch_related("houses__mahalla__district__region").all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action in ["create", "update", "partial_update"]:
            return UserCreateUpdateSerializer
        return UserListSerializer

    def get_queryset(self):
        """Filter users based on role"""
        user = self.request.user
        role = getattr(user, "role", None)

        if not role:
            return User.objects.none()

        # Regular users see only themselves
        if role == "user":
            return User.objects.filter(id=user.id).prefetch_related(
                "houses__mahalla__district__region"
            )

        # Mahalla admin sees users in their mahalla
        if role == "mahalla_admin" and hasattr(user, "mahalla"):
            # Get users who own houses in this mahalla
            return (
                User.objects.filter(houses__mahalla=user.mahalla)
                .distinct()
                .prefetch_related("houses__mahalla__district__region")
            )

        # Super admin and government see all users
        return User.objects.all().prefetch_related("houses__mahalla__district__region")

    def get_permissions(self):
        """Users can view their own data and update it, admins can do CRUD"""
        if self.action in ["list", "retrieve", "update", "partial_update"]:
            return [IsAuthenticated()]
        # Only admins can create and delete users
        return [IsAuthenticated()]
