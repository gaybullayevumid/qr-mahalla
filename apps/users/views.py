from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from .models import OTP, User
from .serializers import SendOTPSerializer, VerifyOTPSerializer, UserSerializer


def send_sms(phone, code):
    print(f"SMS to {phone}: OTP code = {code}")


class SendOTPView(APIView):
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]

        code = OTP.generate_code()
        OTP.objects.create(phone=phone, code=code)

        send_sms(phone, code)

        return Response({"message": "OTP code sent"}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        code = serializer.validated_data["code"]

        try:
            otp = OTP.objects.filter(phone=phone, code=code, is_used=False).latest(
                "created_at"
            )
        except OTP.DoesNotExist:
            return Response(
                {"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST
            )

        if otp.is_expired():
            return Response(
                {"error": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST
            )

        otp.is_used = True
        otp.save()

        user, created = User.objects.get_or_create(phone=phone)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "is_new_user": created,
            }
        )
