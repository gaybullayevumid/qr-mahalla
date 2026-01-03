from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import ScanLog
from .serializers import ScanLogSerializer


class ScanLogViewSet(ReadOnlyModelViewSet):
    """ViewSet for viewing scan logs (read-only)."""

    queryset = ScanLog.objects.select_related("qr", "qr__house", "scanned_by").all()
    serializer_class = ScanLogSerializer
    permission_classes = [AllowAny]  # Temporarily for testing

    def get_queryset(self):
        """Filter scans based on user role."""
        user = self.request.user
        queryset = super().get_queryset()

        # If no authenticated user, return all (for testing)
        if not user or not user.is_authenticated:
            return queryset

        role = getattr(user, "role", None)

        # Client sees only their own scans
        if role == "client":
            return queryset.filter(scanned_by=user)

        # Leader sees scans in their mahalla
        if role == "leader" and hasattr(user, "mahalla"):
            return queryset.filter(qr__house__mahalla=user.mahalla)

        # Admin and gov see all
        return queryset
