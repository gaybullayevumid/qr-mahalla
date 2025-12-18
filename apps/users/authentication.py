from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User


class PhoneAuthentication(BaseAuthentication):
    """
    Telefon raqam orqali autentifikatsiya (vaqtinchalik)
    Authorization: Phone +998901234567
    """

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        print(f"DEBUG: Auth header = '{auth_header}'")

        if not auth_header:
            return None

        # "Phone +998901234567" formatini tekshirish
        parts = auth_header.split()

        print(f"DEBUG: Parts = {parts}")

        if len(parts) != 2 or parts[0].lower() != "phone":
            return None

        phone = parts[1]

        print(f"DEBUG: Looking for phone = '{phone}'")

        try:
            user = User.objects.get(phone=phone)
            print(f"DEBUG: User found = {user.phone}, Role = {user.role}")
            return (user, None)
        except User.DoesNotExist:
            print(f"DEBUG: User not found!")
            raise AuthenticationFailed("Foydalanuvchi topilmadi")

    def authenticate_header(self, request):
        return "Phone"
