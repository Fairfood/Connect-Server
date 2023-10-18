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
    queryset = catalog_models.Country.objects.all().prefetch_related(
        "currency",
        "provinces",
        "provinces__regions",
        "provinces__regions__villages",
    )


class ProvinceViewSet(IdDecodeModelViewSet):
    """View to list, create and update Province data."""

    http_method_names = [
        "get",
    ]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = [
        "name",
    ]
    filterset_class = catalog_filters.ProvinceFilter
    serializer_class = country_serializer.BaseProvinceSerializer
    queryset = catalog_models.Province.objects.all().prefetch_related(
        "regions", "regions__villages"
    )


class RegionViewSet(IdDecodeModelViewSet):
    """View to list, create and update Region data."""

    http_method_names = [
        "get",
    ]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = [
        "name",
    ]
    filterset_class = catalog_filters.RegionFilter
    serializer_class = country_serializer.BaseRegionSerializer
    queryset = catalog_models.Region.objects.all().prefetch_related("villages")


class VillageViewSet(IdDecodeModelViewSet):
    """View to list, create and update Village data."""

    http_method_names = ["get", "post"]
    filterset_class = catalog_filters.VillageFilter
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = [
        "name",
    ]
    serializer_class = country_serializer.VillageSerializer
    queryset = catalog_models.Village.objects.all()
