from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import RegionViewSet, DistrictViewSet, MahallaViewSet
from .export_views import ExportHousesView

router = DefaultRouter()
router.register("regions", RegionViewSet, basename="region")
router.register("districts", DistrictViewSet, basename="district")
router.register(
    "neighborhoods", MahallaViewSet, basename="mahalla"
)  # URL is neighborhoods, but basename is mahalla for admin

urlpatterns = [
    path('export/houses/', ExportHousesView.as_view(), name='export-houses'),
] + router.urls
