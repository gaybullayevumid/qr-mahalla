from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView
)
from rest_framework.permissions import IsAuthenticated

from .models import OwnerProfile
from .serializers import OwnerProfileSerializer


class OwnerProfileCreateView(CreateAPIView):
    serializer_class = OwnerProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OwnerProfileDetailView(RetrieveAPIView):
    serializer_class = OwnerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return OwnerProfile.objects.get(user=self.request.user)


class OwnerProfileUpdateView(UpdateAPIView):
    serializer_class = OwnerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return OwnerProfile.objects.get(user=self.request.user)
