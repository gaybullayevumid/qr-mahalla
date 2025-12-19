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
from .permissions import IsSuperAdmin


class RegionViewSet(ModelViewSet):
    queryset = Region.objects.prefetch_related("districts__mahallas__admin").all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return RegionCreateSerializer
        # Use detailed serializer for both list and retrieve
        return RegionDetailSerializer


class DistrictViewSet(ModelViewSet):
    queryset = District.objects.select_related("region").all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return DistrictCreateSerializer
        return DistrictSerializer
    
    def create(self, request, *args, **kwargs):
        print(f"📥 District POST data: {request.data}")
        print(f"👤 User: {request.user}")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            print(f"✅ District created: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(f"❌ Validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MahallaViewSet(ModelViewSet):
    queryset = Mahalla.objects.select_related("district", "admin").all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return MahallaCreateSerializer
        return MahallaSerializer
