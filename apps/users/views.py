from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, PhoneOTP
from .serializers import RegisterSerializer, VerifyOTPSerializer
from .services import send_sms


class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]

        user, created = User.objects.get_or_create(phone=phone)

        code = PhoneOTP.generate_code()
        PhoneOTP.objects.create(phone=phone, code=code)

        send_sms(phone, code)

        return Response({"message": "SMS kod yuborildi"}, status=status.HTTP_200_OK)


class VerifyOTPAPIView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        code = serializer.validated_data["code"]

        otp = PhoneOTP.objects.filter(phone=phone, code=code, is_used=False).last()

        if not otp or otp.is_expired():
            return Response(
                {"error": "Kod noto‘g‘ri yoki eskirgan"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp.is_used = True
        otp.save()

        user = User.objects.get(phone=phone)
        user.is_verified = True
        user.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "role": user.role,
            }
        )
