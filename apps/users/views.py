from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, PhoneOTP
from .serializers import RegisterSerializer, VerifyOTPSerializer
from .services import send_sms


class RegisterAPIView(APIView):
    """
    Telefon raqam orqali ro'yxatdan o'tish va SMS kod yuborish
    """

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]

        # Foydalanuvchi yaratish yoki olish
        user, created = User.objects.get_or_create(phone=phone)

        # Eski kodlarni bekor qilish
        PhoneOTP.objects.filter(phone=phone, is_used=False).update(is_used=True)

        # Yangi kod yaratish
        code = PhoneOTP.generate_code()
        PhoneOTP.objects.create(phone=phone, code=code)

        # SMS yuborish
        try:
            send_sms(phone, code)
            return Response(
                {"message": "SMS kod yuborildi", "phone": phone},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": "SMS yuborishda xatolik yuz berdi"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class VerifyOTPAPIView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        code = serializer.validated_data["code"]

        # Foydalanuvchi mavjudligini tekshirish
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response(
                {"error": "Foydalanuvchi topilmadi"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # OTP kodni tekshirish
        otp = (
            PhoneOTP.objects.filter(phone=phone, code=code, is_used=False)
            .order_by("-created_at")
            .first()
        )

        if not otp:
            return Response(
                {"error": "Kod noto'g'ri yoki allaqachon ishlatilgan"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if otp.is_expired():
            return Response(
                {"error": "Kod muddati tugagan. Iltimos, qaytadan kod oling"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # OTP kodni ishlatilgan deb belgilash
        otp.is_used = True
        otp.save()

        # Foydalanuvchini tasdiqlash
        user.is_verified = True
        user.save()

        # JWT token yaratish
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "phone": user.phone,
                    "role": user.role,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
            },
            status=status.HTTP_200_OK,
        )


class UserProfileAPIView(APIView):
    """
    Foydalanuvchi profilini ko'rish
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not user.is_authenticated or not hasattr(user, "role"):
            return Response(
                {"error": "Autentifikatsiya talab qilinadi"},
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
            }
        )
