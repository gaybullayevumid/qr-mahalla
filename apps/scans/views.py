from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from .models import ScanLog
from .serializers import ScanLogSerializer


# Foydalanuvchi o‘z scan tarixini ko‘rishi mumkin
class MyScanLogListView(ListAPIView):
    serializer_class = ScanLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ScanLog.objects.filter(scanned_by=self.request.user)
