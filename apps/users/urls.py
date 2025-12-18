from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserProfileAPIView, AuthAPIView

urlpatterns = [
    path("auth/", AuthAPIView.as_view(), name="auth"),
    path("profile/", UserProfileAPIView.as_view(), name="profile"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
