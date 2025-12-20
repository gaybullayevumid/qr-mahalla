from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import House
from .serializers import HouseSerializer, HouseCreateSerializer
from .permissions import HouseAccessPermission


class HouseViewSet(ModelViewSet):
    """CRUD operations for houses"""

    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Allow read and create for all, update/delete for admins only"""
        if self.action in ["list", "retrieve", "create"]:
            return [IsAuthenticated()]
        return [IsAuthenticated(), HouseAccessPermission()]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return HouseCreateSerializer
        return HouseSerializer

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "role", None)

        if not role:
            return House.objects.none()

        queryset = House.objects.select_related("owner", "mahalla__district__region")

        # Regular users see all houses (read-only)
        if role == "user":
            return queryset

        # Owner sees their own houses
        if role == "owner":
            return queryset.filter(owner=user)

        # Mahalla admin sees their neighborhood
        if role == "mahalla_admin" and hasattr(user, "mahalla"):
            return queryset.filter(mahalla=user.mahalla)

        # Super admin and government see all
        return queryset
