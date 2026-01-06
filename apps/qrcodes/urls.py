from django.urls import path
from .views import (
    ScanQRCodeView,
    ClaimHouseView,
    QRCodeListAPIView,
    QRCodeCreateAPIView,
    QRCodeDetailAPIView,
    QRCodeScanAPIView,
    BulkQRCodeGenerateView,
    QRCodeBulkListView,
)

urlpatterns = [
    path("scan/", QRCodeScanAPIView.as_view(), name="qr-scan-post"),
    path("", QRCodeListAPIView.as_view(), name="qr-list"),
    path("create/", QRCodeCreateAPIView.as_view(), name="qr-create"),
    path("bulk/generate/", BulkQRCodeGenerateView.as_view(), name="qr-bulk-generate"),
    path("bulk/list/", QRCodeBulkListView.as_view(), name="qr-bulk-list"),
    path("<str:uuid>/", QRCodeDetailAPIView.as_view(), name="qr-detail"),
    path("scan/<str:uuid>/", ScanQRCodeView.as_view(), name="qr-scan"),
    path("claim/<str:uuid>/", ClaimHouseView.as_view(), name="qr-claim"),
]
