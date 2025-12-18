from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User


class PhoneAuthentication(BaseAuthentication):
    """
    Authentication via phone number (temporary)
    Authorization: Phone +998901234567
    """

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        print(f"DEBUG: Auth header = '{auth_header}'")

        if not auth_header:
            return None

        # Check "Phone +998901234567" format OR just "+998901234567"
        parts = auth_header.split()

        print(f"DEBUG: Parts = {parts}")

        # If format is "Phone +998901234567"
        if len(parts) == 2 and parts[0].lower() == "phone":
            phone = parts[1]
        # If format is just "+998901234567"
        elif len(parts) == 1 and parts[0].startswith("+998"):
            phone = parts[0]
        else:
            return None

        print(f"DEBUG: Looking for phone = '{phone}'")

        try:
            user = User.objects.get(phone=phone)
            print(f"DEBUG: User found = {user.phone}, Role = {user.role}")
            return (user, None)
        except User.DoesNotExist:
            print(f"DEBUG: User not found!")
            raise AuthenticationFailed("User not found")

    def authenticate_header(self, request):
        return "Phone"
