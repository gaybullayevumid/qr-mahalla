from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from .models import Region, District, Mahalla
from .serializers import (
    RegionSerializer,
    RegionWriteSerializer,
    RegionDetailSerializer,
    DistrictSerializer,
    DistrictCreateSerializer,
    DistrictNestedSerializer,
    DistrictNestedWriteSerializer,
    MahallaSerializer,
    MahallaCreateSerializer,
    MahallaNestedWriteSerializer,
)
from .permissions import IsAdmin, IsAdminOrGov


class RegionViewSet(ModelViewSet):
    queryset = Region.objects.prefetch_related(
        "districts__mahallas__admin", "districts__mahallas__houses__owner"
    ).all()

    def get_permissions(self):
        """
        Allow all authenticated users to view (GET) regions
        Only admins can create/update/delete
        """
        if self.action in ["list", "retrieve", "districts", "neighborhoods"]:
            return [IsAuthenticated()]
        return [IsAdminOrGov()]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return RegionWriteSerializer
        # Use detailed serializer for both list and retrieve
        return RegionDetailSerializer

    @action(detail=True, methods=["get", "post"], url_path="districts")
    def districts(self, request, pk=None):
        """
        GET: List all districts in this region
        POST: Create a new district in this region
        """
        region = self.get_object()

        if request.method == "GET":
            districts = District.objects.filter(region=region).prefetch_related(
                "mahallas__admin"
            )
            serializer = DistrictNestedSerializer(districts, many=True)
            return Response(serializer.data)

        elif request.method == "POST":
            # Create district in this region
            serializer = DistrictNestedWriteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(region=region)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"], url_path="neighborhoods")
    def neighborhoods(self, request, pk=None):
        """
        GET: List all neighborhoods in this region
        POST: Not supported (create neighborhoods under districts)
        """
        region = self.get_object()

        if request.method == "GET":
            mahallas = Mahalla.objects.filter(district__region=region).select_related(
                "district", "admin"
            )
            serializer = MahallaSerializer(mahallas, many=True)
            return Response(serializer.data)

        elif request.method == "POST":
            return Response(
                {
                    "error": "Create neighborhoods under districts endpoint: /api/districts/{id}/neighborhoods/"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class DistrictViewSet(ModelViewSet):
    queryset = (
        District.objects.select_related("region")
        .prefetch_related("mahallas__admin")
        .all()
    )

    def get_permissions(self):
        """
        Allow all authenticated users to view (GET) districts
        Only admins can create/update/delete
        """
        if self.action in ["list", "retrieve", "neighborhoods"]:
            return [IsAuthenticated()]
        return [IsAdminOrGov()]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return DistrictNestedWriteSerializer  # Supports nested mahallas CRUD
        if self.action == "retrieve":
            return DistrictNestedSerializer  # Shows nested mahallas on detail view
        return DistrictSerializer

    @action(detail=True, methods=["get", "post"], url_path="neighborhoods")
    def neighborhoods(self, request, pk=None):
        """
        GET: List all neighborhoods in this district
        POST: Create a new neighborhood in this district
        """
        district = self.get_object()

        if request.method == "GET":
            mahallas = Mahalla.objects.filter(district=district).select_related("admin")
            serializer = MahallaSerializer(mahallas, many=True)
            return Response(serializer.data)

        elif request.method == "POST":
            # Create neighborhood in this district
            data = request.data.copy()
            data["district"] = district.id  # Auto-set district from URL
            serializer = MahallaCreateSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class MahallaViewSet(ModelViewSet):
    queryset = Mahalla.objects.select_related("district", "admin").all()

    def get_permissions(self):
        """
        Allow regular users to list/retrieve mahallas for house creation
        Only admins can create/update/delete
        """
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsAdminOrGov()]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return MahallaCreateSerializer
        return MahallaSerializer
