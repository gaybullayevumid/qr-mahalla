from django.urls import path
from .views import RegionListView, DistrictListView, MahallaListView

urlpatterns = [
    path("regions/", RegionListView.as_view(), name="regions"),
    path(
        "regions/<int:region_id>/districts/",
        DistrictListView.as_view(),
        name="districts",
    ),
    path(
        "districts/<int:district_id>/mahallas/",
        MahallaListView.as_view(),
        name="mahallas",
    ),
]
