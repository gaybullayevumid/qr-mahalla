from django.urls import path
from .views import (
    OwnerProfileCreateView,
    OwnerProfileDetailView,
    OwnerProfileUpdateView,
)

urlpatterns = [
    path("owners/profile/", OwnerProfileCreateView.as_view()),
    path("owners/profile/me/", OwnerProfileDetailView.as_view()),
    path("owners/profile/update/", OwnerProfileUpdateView.as_view()),
]
