from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserProfileAPIView,
    AuthAPIView,
    UserSessionsAPIView,
    LogoutDeviceAPIView,
    LogoutAllDevicesAPIView,
    UserRolesAPIView,
)

urlpatterns = [
    path("auth/", AuthAPIView.as_view(), name="auth"),
    path("profile/", UserProfileAPIView.as_view(), name="profile"),
    path("roles/", UserRolesAPIView.as_view(), name="roles"),
    path("sessions/", UserSessionsAPIView.as_view(), name="sessions"),
    path("logout-device/", LogoutDeviceAPIView.as_view(), name="logout-device"),
    path("logout-all/", LogoutAllDevicesAPIView.as_view(), name="logout-all"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
