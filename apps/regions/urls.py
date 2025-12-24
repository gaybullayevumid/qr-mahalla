from rest_framework.routers import DefaultRouter
from .views import RegionViewSet

router = DefaultRouter()
router.register(
    "", RegionViewSet, basename="region"
)  # Empty string instead of "regions"

urlpatterns = router.urls
