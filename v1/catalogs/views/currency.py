"""Views realated to country model are stored here."""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from base.request_handler.views import IDDEcodeScopeViewset
from v1.catalogs import filters as catalog_filters
from v1.catalogs.models import common_models as catalog_models
from v1.catalogs.serializers import currency as currency_serializers

# from v1.apiauth import permissions as auth_permissions


class CurrencyViewSet(IDDEcodeScopeViewset):
    """View to list, create and update country data."""

    http_method_names = [
        "get",
    ]
    filterset_class = catalog_filters.CurrencyFilterSet
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = [
        "name",
        "code",
    ]
    resource_types = ["catalog"]
    serializer_class = currency_serializers.CurrencySerializer
    queryset = catalog_models.Currency.objects.all()
