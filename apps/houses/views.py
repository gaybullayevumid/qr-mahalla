from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import House
from .serializers import HouseSerializer, HouseCreateSerializer
from .permissions import HouseAccessPermission


class HouseViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Allow regular users to read (GET), only admins/owners can modify
        """
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), HouseAccessPermission()]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return HouseCreateSerializer
        return HouseSerializer

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated or not hasattr(user, "role"):
            return House.objects.none()

        # Regular users can see houses in their mahalla (but cannot modify)
        if user.role == "user":
            return House.objects.all()

        if user.role == "super_admin":
            return House.objects.all()

        if user.role == "mahalla_admin" and hasattr(user, "mahalla"):
            return House.objects.filter(mahalla=user.mahalla)

        if user.role == "owner":
            return House.objects.filter(owner=user)

        if user.role == "government":
            return House.objects.all()

        return House.objects.none()
