from django.urls import path
from .views import (
    QRScanAPIView,
    QRCodeListAPIView,
    QRCodeCreateAPIView,
    QRCodeDetailAPIView,
    QRCodeClaimAPIView,
)

urlpatterns = [
    path("", QRCodeListAPIView.as_view(), name="qrcode-list"),
    path("create/", QRCodeCreateAPIView.as_view(), name="qrcode-create"),
    path("<str:qr_id>/", QRCodeDetailAPIView.as_view(), name="qrcode-detail"),
    path("scan/<str:qr_id>/", QRScanAPIView.as_view(), name="qrcode-scan"),
    path("claim/<str:qr_id>/", QRCodeClaimAPIView.as_view(), name="qrcode-claim"),
]
