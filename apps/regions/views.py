from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny

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
from .permissions import IsSuperAdmin


class RegionViewSet(ModelViewSet):
    queryset = Region.objects.prefetch_related("districts__mahallas__admin").all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return RegionCreateSerializer
        elif self.action == "retrieve":
            return RegionDetailSerializer
        return RegionSerializer


class DistrictViewSet(ModelViewSet):
    queryset = District.objects.select_related("region").all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return DistrictCreateSerializer
        return DistrictSerializer


class MahallaViewSet(ModelViewSet):
    queryset = Mahalla.objects.select_related("district", "admin").all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return MahallaCreateSerializer
        return MahallaSerializer
