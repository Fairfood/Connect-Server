"""URLs of the app accounts."""
from django.urls import path
from rest_framework import routers

from v1.accounts.views import user as user_views
from v1.accounts.views import utils as utility_views

router = routers.SimpleRouter()

router.register(r"users", user_views.UserViewSet, basename="users")

urlpatterns = router.urls

urlpatterns += [
    path(
        "privacy-policy/",
        user_views.PrivacyPolicy.as_view(),
        name="get_privacy_policy",
    ),
    path(
        "countries-with-provinces/",
        utility_views.CountryWithProvincesListView.as_view({'get': 'list'}),
        name="countries_with_provinces",
    ),
    path(
        "countries/",
        utility_views.CountryListView.as_view({'get': 'list'}),
        name="countries",
    ),
    path(
        "provinces/<str:country_name>/",
        utility_views.CountryWithProvincesListView.as_view({'get': 'retrieve'}),
        name="provinces",
    ),
]
