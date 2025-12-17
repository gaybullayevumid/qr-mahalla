from rest_framework.generics import ListAPIView
from .models import Region, District, Mahalla
from .serializers import RegionSerializer, DistrictSerializer, MahallaSerializer


# Viloyatlar ro‘yxati
class RegionListView(ListAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer


# Tanlangan viloyatga tegishli tumanlar
class DistrictListView(ListAPIView):
    serializer_class = DistrictSerializer

    def get_queryset(self):
        region_id = self.kwargs["region_id"]
        return District.objects.filter(region_id=region_id)


# Tanlangan tumanga tegishli mahallalar
class MahallaListView(ListAPIView):
    serializer_class = MahallaSerializer

    def get_queryset(self):
        district_id = self.kwargs["district_id"]
        return Mahalla.objects.filter(district_id=district_id)
