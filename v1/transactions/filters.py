from django.db.models import Count
from django.db.models import Q
from django_filters import rest_framework as filters

from .models import payment_models
from .models import transaction_models
from base.authentication import utilities as auth_utils
from utilities.functions import unix_to_datetime
from v1.transactions.constants import PaymentType


class ProductTransactionFilterSet(filters.FilterSet):
    """A filter set for the Farmer model.

    This filter set allows filtering of Product Transaction objects.
    """

    # TODO: Change this filter after informing the frontend.
    updated_after = filters.NumberFilter(
        method="updated_after_filter", field_name="created_on"
    )
    created_after = filters.NumberFilter(
        method="updated_after_filter", field_name="created_on"
    )
    updated_before = filters.NumberFilter(
        method="updated_before_filter", field_name="created_on"
    )
    only_quantity_available = filters.BooleanFilter(
        method="quantity_available_filter"
    )

    class Meta:
        model = transaction_models.ProductTransaction
        fields = []

    @property
    def qs(self):
        """Return queryset."""
        parent = super().qs

        # Skip filters for admin
        user = auth_utils.get_current_user()
        if user.is_admin:
            return parent

        entity = auth_utils.get_current_entity()
        return parent.filter(
            Q(source=entity, creator=user)
            | Q(destination=entity, creator=user)
        )

    def updated_after_filter(self, queryset, name, value):
        """Return queryset."""
        name += "__gte"
        value = unix_to_datetime(value)
        return queryset.filter(**{name: value})

    def updated_before_filter(self, queryset, name, value):
        """Return queryset."""
        name += "__lt"
        value = unix_to_datetime(value)
        return queryset.filter(**{name: value})

    def quantity_available_filter(self, queryset, name, value):
        """Return queryset."""
        if value or value == "true":
            entity = auth_utils.get_current_entity()
            return queryset.annotate(total_children=Count("children")).filter(
                total_children=0, destination=entity, quantity__gt=0
            )
        return queryset


class PaymentTransactionFilterSet(filters.FilterSet):
    """A filter set for the Farmer model.

    This filter set allows filtering of Payment Transaction objects.
    """

    updated_after = filters.NumberFilter(
        method="updated_after_filter", field_name="created_on"
    )

    class Meta:
        model = payment_models.PaymentTransaction
        fields = ["payment_type"]

    @property
    def qs(self):
        """Return queryset."""
        parents = super().qs
        # Skip filters for admin
        user = auth_utils.get_current_user()
        if user.is_admin:
            return parents.filter(payment_type=PaymentType.PREMIUM)

        entity = auth_utils.get_current_entity()
        parents = parents.filter(Q(source=entity) | Q(destination=entity))
        return parents.filter(payment_type=PaymentType.PREMIUM)

    def updated_after_filter(self, queryset, name, value):
        """Return queryset."""
        name += "__gte"
        value = unix_to_datetime(value)
        return queryset.filter(**{name: value})
