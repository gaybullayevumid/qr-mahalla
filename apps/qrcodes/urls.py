from django.urls import path
from .views import QRScanAPIView

urlpatterns = [
    path("scan/<str:qr_id>/", QRScanAPIView.as_view()),
]
