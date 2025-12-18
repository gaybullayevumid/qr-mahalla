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

        if not auth_header:
            return None

        # Check "Phone +998901234567" format OR just "+998901234567"
        parts = auth_header.split()

        # If format is "Phone +998901234567"
        if len(parts) == 2 and parts[0].lower() == "phone":
            phone = parts[1]
        # If format is just "+998901234567"
        elif len(parts) == 1 and parts[0].startswith("+998"):
            phone = parts[0]
        else:
            return None

        try:
            user = User.objects.get(phone=phone)
            return (user, None)
        except User.DoesNotExist:
            # Return None so JWT authentication can be tried next
            return None

    def authenticate_header(self, request):
        return "Phone"
