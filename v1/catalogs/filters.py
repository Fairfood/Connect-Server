"""Filters used in the catalogs api."""
from django_filters import rest_framework as filters

from base.authentication import utilities as utils
from utilities.functions import unix_to_datetime
from v1.catalogs.models import common_models as catalog_models

from .models import product_models


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


class ProductFilterSet(filters.FilterSet):
    """Filterclass for product-list api."""

    updated_after = filters.NumberFilter(
        method="updated_after_filter", field_name="updated_on"
    )
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")

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

    def updated_after_filter(self, queryset, name, value):
        """Return queryset."""
        name += "__gte"
        value = unix_to_datetime(value)
        return queryset.filter(**{name: value})


class PremiumFilterSet(filters.FilterSet):
    """Filterclass for product-list api."""

    updated_after = filters.NumberFilter(
        method="updated_after_filter", field_name="updated_on"
    )
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    class Meta:
        """Meta Info."""

        model = product_models.Premium
        fields = ("name", "updated_after",)

    @property
    def qs(self):
        """Return queryset."""
        parent = super().qs
        entity = utils.get_current_entity()
        return parent.filter(
            owner__in=[entity, entity.buyer if entity else None]
        )

    def updated_after_filter(self, queryset, name, value):
        """Return queryset."""
        name += "__gte"
        value = unix_to_datetime(value)
        return queryset.filter(**{name: value})
