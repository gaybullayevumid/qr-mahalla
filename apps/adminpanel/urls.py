from django.urls import path
from .views import (
    AdminUserListView,
    AdminUserRoleUpdateView,
    AdminQRCodeListView,
    AdminScanLogListView
)

urlpatterns = [
    path("admin/users/", AdminUserListView.as_view()),
    path("admin/users/<int:id>/role/", AdminUserRoleUpdateView.as_view()),
    path("admin/qrcodes/", AdminQRCodeListView.as_view()),
    path("admin/scans/", AdminScanLogListView.as_view()),
]
