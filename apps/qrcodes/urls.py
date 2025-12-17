from django.urls import path
from .views import QRScanView

urlpatterns = [
    path("scan/<uuid:qr_id>/", QRScanView.as_view(), name="qr-scan"),
]
