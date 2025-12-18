from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Region, District, Mahalla
from .serializers import (
    RegionSerializer,
    RegionDetailSerializer,
    DistrictSerializer,
    MahallaSerializer,
)
from .permissions import IsSuperAdmin


class RegionViewSet(ModelViewSet):
    queryset = Region.objects.prefetch_related("districts__mahallas__admin").all()
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get_serializer_class(self):
        # Detail view uchun nested serializer
        if self.action == "retrieve":
            return RegionDetailSerializer
        return RegionSerializer


class DistrictViewSet(ModelViewSet):
    queryset = District.objects.select_related("region").all()
    serializer_class = DistrictSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]


class MahallaViewSet(ModelViewSet):
    queryset = Mahalla.objects.select_related("district", "admin").all()
    serializer_class = MahallaSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]
