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
    Register via phone number and send SMS code
    """

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]

        # Create or get user
        user, created = User.objects.get_or_create(phone=phone)

        # Invalidate old codes
        PhoneOTP.objects.filter(phone=phone, is_used=False).update(is_used=True)

        # Generate new code
        code = PhoneOTP.generate_code()
        PhoneOTP.objects.create(phone=phone, code=code)

        # Send SMS
        try:
            send_sms(phone, code)
            return Response(
                {"message": "SMS code sent", "phone": phone},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": "Error sending SMS"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class VerifyOTPAPIView(APIView):
    """
    Verify SMS code and get token
    """

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        code = serializer.validated_data["code"]

        # Check if user exists
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check OTP code
        otp = (
            PhoneOTP.objects.filter(phone=phone, code=code, is_used=False)
            .order_by("-created_at")
            .first()
        )

        if not otp:
            return Response(
                {"error": "Code is incorrect or already used"},
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

        # Verify user
        user.is_verified = True
        user.save()

        # Create JWT token
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
    Get user profile
    """

    permission_classes = [IsAuthenticated]

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
            }
        )
