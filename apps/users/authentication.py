from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User


class PhoneAuthentication(BaseAuthentication):
    """
    Custom authentication backend using phone number.

    Supports two authorization header formats:
    - "Phone +998901234567"
    - "+998901234567"

    Falls back to JWT authentication if phone authentication fails.
    Note: This is a temporary authentication method.
    """

    def authenticate(self, request):
        """Authenticate user by phone number from authorization header."""
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if not auth_header:
            return None

        parts = auth_header.split()

        if len(parts) == 2 and parts[0].lower() == "phone":
            phone = parts[1]
        elif len(parts) == 1 and parts[0].startswith("+998"):
            phone = parts[0]
        else:
            return None

        try:
            user = User.objects.get(phone=phone)
            return (user, None)
        except User.DoesNotExist:
            return None

    def authenticate_header(self, request):
        """Return the authentication scheme name."""
        return "Phone"
