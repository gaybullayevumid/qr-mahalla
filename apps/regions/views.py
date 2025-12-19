from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import Region, District, Mahalla
from .serializers import (
    RegionSerializer,
    RegionCreateSerializer,
    RegionDetailSerializer,
    DistrictSerializer,
    DistrictCreateSerializer,
    MahallaSerializer,
    MahallaCreateSerializer,
)
from .permissions import IsSuperAdmin, IsAdminOrGovernment


class RegionViewSet(ModelViewSet):
    queryset = Region.objects.prefetch_related("districts__mahallas__admin").all()

    def get_permissions(self):
        """
        Allow regular users to read (GET), only admins can modify
        """
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminOrGovernment()]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return RegionCreateSerializer
        # Use detailed serializer for both list and retrieve
        return RegionDetailSerializer


class DistrictViewSet(ModelViewSet):
    queryset = District.objects.select_related("region").all()

    def get_permissions(self):
        """
        Allow regular users to read (GET), only admins can modify
        """
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminOrGovernment()]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return DistrictCreateSerializer
        return DistrictSerializer


class MahallaViewSet(ModelViewSet):
    queryset = Mahalla.objects.select_related("district", "admin").all()

    def get_permissions(self):
        """
        Allow regular users to read (GET) and create (POST)
        Only admins can update/delete
        """
        if self.action in ['list', 'retrieve', 'create']:
            return [IsAuthenticated()]
        return [IsAdminOrGovernment()]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return MahallaCreateSerializer
        return MahallaSerializer
