from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScanLogViewSet

router = DefaultRouter()
router.register(r'', ScanLogViewSet, basename='scanlogs')

urlpatterns = [
    path('', include(router.urls)),
]
