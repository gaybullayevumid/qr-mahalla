from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import Region, District, Mahalla
from .serializers import (
    RegionSerializer,
    RegionWriteSerializer,
    RegionDetailSerializer,
    DistrictSerializer,
    DistrictCreateSerializer,
    MahallaSerializer,
    MahallaCreateSerializer,
)
from .permissions import IsSuperAdmin, IsAdminOrGovernment


class RegionViewSet(ModelViewSet):
    queryset = Region.objects.prefetch_related(
        "districts__mahallas__admin", "districts__mahallas__houses__owner"
    ).all()

    def get_permissions(self):
        """
        Allow all authenticated users to view (GET) regions
        Only admins can create/update/delete
        """
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsAdminOrGovernment()]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return RegionWriteSerializer
        # Use detailed serializer for both list and retrieve
        return RegionDetailSerializer


class DistrictViewSet(ModelViewSet):
    queryset = District.objects.select_related("region").all()

    def get_permissions(self):
        """
        Allow all authenticated users to view (GET) districts
        Only admins can create/update/delete
        """
        if self.action in ["list", "retrieve"]:
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
        Allow regular users to list/retrieve mahallas for house creation
        Only admins can create/update/delete
        """
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsAdminOrGovernment()]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return MahallaCreateSerializer
        return MahallaSerializer
