from django.urls import path
from .views import MyScanLogListView

urlpatterns = [
    path("scans/my/", MyScanLogListView.as_view()),
]
