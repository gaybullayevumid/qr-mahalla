from rest_framework.generics import (
    ListAPIView,
    UpdateAPIView
)
from .permissions import IsAdmin
from .serializers import (
    UserAdminSerializer,
    UserRoleUpdateSerializer,
    QRCodeAdminSerializer,
    ScanLogAdminSerializer
)

from apps.users.models import User
from apps.qrcodes.models import QRCode
from apps.scans.models import ScanLog


# 👤 Foydalanuvchilar ro‘yxati
class AdminUserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = [IsAdmin]


# 🔁 Rol o‘zgartirish
class AdminUserRoleUpdateView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRoleUpdateSerializer
    permission_classes = [IsAdmin]
    lookup_field = "id"


# 🔲 QR code nazorati
class AdminQRCodeListView(ListAPIView):
    queryset = QRCode.objects.all()
    serializer_class = QRCodeAdminSerializer
    permission_classes = [IsAdmin]


# 📷 Scan loglar
class AdminScanLogListView(ListAPIView):
    queryset = ScanLog.objects.select_related("qr", "scanned_by")
    serializer_class = ScanLogAdminSerializer
    permission_classes = [IsAdmin]
