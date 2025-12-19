from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import House
from .serializers import HouseSerializer, HouseCreateSerializer
from .permissions import HouseAccessPermission


class HouseViewSet(ModelViewSet):
    permission_classes = [AllowAny]  # Temporarily disabled for testing

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return HouseCreateSerializer
        return HouseSerializer

    def get_queryset(self):
        # Return all houses for testing
        return House.objects.all()
