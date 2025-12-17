from django.urls import path
from .views import SendOTPView, VerifyOTPView

urlpatterns = [
    path("auth/send-otp/", SendOTPView.as_view()),
    path("auth/verify-otp/", VerifyOTPView.as_view()),
]
