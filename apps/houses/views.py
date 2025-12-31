from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import House
from .serializers import HouseSerializer, HouseCreateSerializer
from .permissions import HouseAccessPermission


class HouseViewSet(ModelViewSet):
    """ViewSet for CRUD operations on houses."""

    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Return permissions based on action.

        Allow read and create for all authenticated users.
        Update and delete operations require HouseAccessPermission.
        """
        if self.action in ["list", "retrieve", "create"]:
            return [IsAuthenticated()]
        return [IsAuthenticated(), HouseAccessPermission()]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return HouseCreateSerializer
        return HouseSerializer

    def perform_create(self, serializer):
        """Set the owner to the current user when creating a house."""
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "role", None)

        if not role:
            return House.objects.none()

        queryset = House.objects.select_related("owner", "mahalla__district__region")

        if role == "client":
            return queryset.filter(owner=user)

        if role == "leader" and hasattr(user, "mahalla"):
            return queryset.filter(mahalla=user.mahalla)

        return queryset
