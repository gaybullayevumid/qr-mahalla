from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Region, District, Mahalla
from .serializers import RegionSerializer, DistrictSerializer, MahallaSerializer
from .permissions import IsSuperAdmin


class RegionViewSet(ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]


class DistrictViewSet(ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]


class MahallaViewSet(ModelViewSet):
    queryset = Mahalla.objects.all()
    serializer_class = MahallaSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]
