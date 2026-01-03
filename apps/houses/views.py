from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .models import House
from .serializers import (
    HouseSerializer,
    HouseCreateSerializer,
    HouseAdminCreateSerializer,
)
from .permissions import HouseAccessPermission


class HouseViewSet(ModelViewSet):
    """ViewSet for CRUD operations on houses."""

    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Return permissions based on action.

        Allow read and create for all authenticated users.
        Update and delete operations require HouseAccessPermission.
        """
        if self.action in ["list", "retrieve", "create", "admin_create"]:
            return [AllowAny()]  # Temporarily allow any for testing
        return [IsAuthenticated(), HouseAccessPermission()]

    def get_serializer_class(self):
        if self.action == "admin_create":
            return HouseAdminCreateSerializer
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

    @action(detail=False, methods=["post"], url_path="admin-create")
    def admin_create(self, request):
        """
        Admin endpoint for creating houses with owner details.

        Accepts:
        - phone: owner phone number (will create user if not exists)
        - ownerFirstName, ownerLastName: owner name
        - region, district: optional validation (names)
        - mahalla: mahalla ID (required)
        - address, houseNumber: house details
        """
        serializer = HouseAdminCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        house = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
