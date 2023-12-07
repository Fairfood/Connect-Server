"""Views realated to country model are stored here."""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from base.request_handler.views import IdDecodeModelViewSet
from v1.catalogs import filters as catalog_filters
from v1.catalogs.models import common_models as catalog_models
from v1.catalogs.serializers import country as country_serializer

# from v1.apiauth import permissions as auth_permissions


class CountryViewSet(IdDecodeModelViewSet):
    """View to list, create and update country data."""

    http_method_names = [
        "get",
    ]
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "name",
        "code",
        "dial_code",
    ]
    serializer_class = country_serializer.CountrySerializer
    queryset = catalog_models.Country.objects.all()


class ProvinceViewSet(IdDecodeModelViewSet):
    """View to list, create and update Province data."""

    http_method_names = [
        "get",
    ]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = [
        "name",
    ]
    filterset_class = catalog_filters.ProvinceFilterSet
    serializer_class = country_serializer.ProvinceSerializer
    queryset = catalog_models.Province.objects.all()
