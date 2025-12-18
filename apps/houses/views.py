from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import House
from .serializers import HouseSerializer
from .permissions import HouseAccessPermission


class HouseViewSet(ModelViewSet):
    serializer_class = HouseSerializer
    permission_classes = [IsAuthenticated, HouseAccessPermission]

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated or not hasattr(user, 'role'):
            return House.objects.none()

        if user.role == "super_admin":
            return House.objects.all()

        if user.role == "mahalla_admin" and hasattr(user, "mahalla"):
            return House.objects.filter(mahalla=user.mahalla)

        if user.role == "owner":
            return House.objects.filter(owner=user)

        return House.objects.none()
