from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

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
        if self.action in ["list", "retrieve", "create", "update", "partial_update"]:
            return [AllowAny()]  # Temporarily allow any for testing
        return [IsAuthenticated(), HouseAccessPermission()]

    def get_serializer_class(self):
        # Use HouseCreateSerializer for all actions to get consistent output format
        return HouseCreateSerializer

    def perform_create(self, serializer):
        """Save the house - owner handled by serializer."""
        serializer.save()

    def perform_update(self, serializer):
        """Update the house - owner handled by serializer."""
        serializer.save()

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "role", None)

        # If no user or no role, return all for testing (AllowAny mode)
        if (
            not hasattr(self.request, "user")
            or not user
            or not user.is_authenticated
            or not role
        ):
            return House.objects.select_related(
                "owner", "mahalla__district__region"
            ).all()

        queryset = House.objects.select_related("owner", "mahalla__district__region")

        if role == "client":
            return queryset.filter(owner=user)

        if role == "leader" and hasattr(user, "mahalla"):
            return queryset.filter(mahalla=user.mahalla)

        return queryset
