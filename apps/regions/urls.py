from rest_framework.routers import DefaultRouter
from .views import RegionViewSet, DistrictViewSet, MahallaViewSet

router = DefaultRouter()
router.register("regions", RegionViewSet, basename="region")
router.register("districts", DistrictViewSet, basename="district")
router.register(
    "neighborhoods", MahallaViewSet, basename="mahalla"
)  # URL is neighborhoods, but basename is mahalla for admin

urlpatterns = router.urls
