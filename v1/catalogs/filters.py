"""Filters used in the catalogs api."""
from django_filters import rest_framework as filters

from v1.catalogs.models import common_models as catalog_models


class CurrencyFilter(filters.FilterSet):
    """Filterclass for currency-list api."""

    all = filters.BooleanFilter(method="all_filter")

    class Meta:
        """Meta Info."""

        model = catalog_models.Currency
        fields = (
            "name",
            "code",
        )

    def all_filter(self, queryset, name, value):
        """Return all currencies."""
        query = queryset
        if value:
            query = catalog_models.Currency.objects.all()
        return query


class ProvinceFilter(filters.FilterSet):
    """Filterclass for province."""

    class Meta:
        model = catalog_models.Province
        fields = [
            "country",
        ]


class RegionFilter(filters.FilterSet):
    """Filterclass for Region."""

    class Meta:
        model = catalog_models.Region
        fields = [
            "province",
        ]


class VillageFilter(filters.FilterSet):
    """Filterclass for province."""

    class Meta:
        model = catalog_models.Village
        fields = ["region,"]
