from django.urls import path
from .views import (
    ScanQRCodeView,
    ClaimHouseView,
    QRCodeListAPIView,
    QRCodeCreateAPIView,
    QRCodeDetailAPIView,
    QRCodeScanAPIView,
)

urlpatterns = [
    path("scan/", QRCodeScanAPIView.as_view(), name="qr-scan-post"),
    path("", QRCodeListAPIView.as_view(), name="qr-list"),
    path("create/", QRCodeCreateAPIView.as_view(), name="qr-create"),
    path("<str:uuid>/", QRCodeDetailAPIView.as_view(), name="qr-detail"),
    path("scan/<str:uuid>/", ScanQRCodeView.as_view(), name="qr-scan"),
    path("claim/<str:uuid>/", ClaimHouseView.as_view(), name="qr-claim"),
]
