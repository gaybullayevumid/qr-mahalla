from django.urls import path
from .views import (
    QRScanAPIView,
    QRCodeListAPIView,
    QRCodeCreateAPIView,
    QRCodeDetailAPIView,
    QRCodeClaimAPIView,
    QRCodeMarkDeliveredAPIView,
    QRCodeUnmarkDeliveredAPIView,
    QRScanByUUIDAPIView,
    QRCodeClaimByUUIDAPIView,
)

urlpatterns = [
    path("", QRCodeListAPIView.as_view(), name="qrcode-list"),
    path("create/", QRCodeCreateAPIView.as_view(), name="qrcode-create"),
    path("<str:qr_id>/", QRCodeDetailAPIView.as_view(), name="qrcode-detail"),
    path("scan/<str:qr_id>/", QRScanAPIView.as_view(), name="qrcode-scan"),
    path("claim/<str:qr_id>/", QRCodeClaimAPIView.as_view(), name="qrcode-claim"),
    # UUID-based endpoints for regular users (most important)
    path(
        "scan-uuid/<str:uuid>/", QRScanByUUIDAPIView.as_view(), name="qrcode-scan-uuid"
    ),
    path(
        "claim-uuid/<str:uuid>/",
        QRCodeClaimByUUIDAPIView.as_view(),
        name="qrcode-claim-uuid",
    ),
    path(
        "mark-delivered/",
        QRCodeMarkDeliveredAPIView.as_view(),
        name="qrcode-mark-delivered",
    ),
    path(
        "unmark-delivered/",
        QRCodeUnmarkDeliveredAPIView.as_view(),
        name="qrcode-unmark-delivered",
    ),
]
