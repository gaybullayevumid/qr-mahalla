from rest_framework.routers import DefaultRouter
from .views import RegionViewSet

router = DefaultRouter()
router.register("regions", RegionViewSet)

urlpatterns = router.urls
