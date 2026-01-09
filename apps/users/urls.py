from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserProfileAPIView,
    AuthAPIView,
    UserSessionsAPIView,
    LogoutDeviceAPIView,
    LogoutAllDevicesAPIView,
    UserRolesAPIView,
    CustomTokenRefreshView,
    UserViewSet,
    SMSLogViewSet,
    SMSStatisticsAPIView,
)

router = DefaultRouter()
router.register("list", UserViewSet, basename="user")
router.register("sms-logs", SMSLogViewSet, basename="sms-log")

urlpatterns = [
    path("auth/", AuthAPIView.as_view(), name="auth"),
    path("profile/", UserProfileAPIView.as_view(), name="profile"),
    path("roles/", UserRolesAPIView.as_view(), name="roles"),
    path("sessions/", UserSessionsAPIView.as_view(), name="sessions"),
    path("logout-device/", LogoutDeviceAPIView.as_view(), name="logout-device"),
    path("logout-all/", LogoutAllDevicesAPIView.as_view(), name="logout-all"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("sms-statistics/", SMSStatisticsAPIView.as_view(), name="sms-statistics"),
    path("", include(router.urls)),
]
