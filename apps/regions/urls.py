from rest_framework.routers import DefaultRouter
from .views import RegionViewSet, DistrictViewSet, MahallaViewSet

router = DefaultRouter()
router.register("regions", RegionViewSet)
router.register("districts", DistrictViewSet)
router.register("mahallas", MahallaViewSet)

urlpatterns = router.urls
