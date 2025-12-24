from rest_framework.routers import DefaultRouter
from .views import RegionViewSet, DistrictViewSet, MahallaViewSet

router = DefaultRouter()
router.register("regions", RegionViewSet, basename="region")
router.register("districts", DistrictViewSet, basename="district")
router.register("neighborhoods", MahallaViewSet, basename="neighborhood")

urlpatterns = router.urls
