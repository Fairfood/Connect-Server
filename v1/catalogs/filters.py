"""Filters used in the catalogs api."""
from django_filters import rest_framework as filters

from .models import product_models
from base.authentication import utilities as utils
from v1.catalogs.models import common_models as catalog_models


class CurrencyFilterSet(filters.FilterSet):
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


class ProvinceFilterSet(filters.FilterSet):
    """Filterclass for province."""

    class Meta:
        model = catalog_models.Province
        fields = [
            "country",
        ]


class ProductFilterSet(filters.FilterSet):
    """Filterclass for product-list api."""

    updated_after = filters.DateTimeFilter(
        field_name="updated_at", lookup_expr="gt"
    )

    class Meta:
        """Meta Info."""

        model = product_models.Product
        fields = (
            "name",
            "description",
        )

    @property
    def qs(self):
        """Return queryset."""
        parent = super().qs
        entity = utils.get_current_entity()
        return parent.filter(companies=entity)


class PremiumFilterSet(filters.FilterSet):
    """Filterclass for product-list api."""

    updated_after = filters.DateTimeFilter(
        field_name="updated_at", lookup_expr="gt"
    )

    class Meta:
        """Meta Info."""

        model = product_models.Premium
        fields = ("name",)

    @property
    def qs(self):
        """Return queryset."""
        parent = super().qs
        entity = utils.get_current_entity()
        return parent.filter(owner=entity)
