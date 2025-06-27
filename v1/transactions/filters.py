from django.db.models import Count, Q
from django_filters import rest_framework as filters

from base.authentication import utilities as auth_utils
from utilities.functions import decode, unix_to_datetime
from v1.supply_chains.models.base_models import Entity
from v1.transactions.constants import PaymentType
from v1.transactions.models import payment_models, transaction_models


class ProductTransactionFilterSet(filters.FilterSet):
    """A filter set for the Farmer model.

    This filter set allows filtering of Product Transaction objects.
    """

    # TODO: Change this filter after informing the frontend.
    updated_after = filters.NumberFilter(
        method="updated_after_filter", field_name="updated_on"
    )
    created_after = filters.NumberFilter(
        method="updated_after_filter", field_name="created_on"
    )
    updated_before = filters.NumberFilter(
        method="updated_before_filter", field_name="updated_on"
    )
    only_quantity_available = filters.BooleanFilter(method="quantity_available_filter")
    skip_only_connect = filters.BooleanFilter(method="skip_only_connect_filter")
    entity = filters.CharFilter(method="entity_filter")

    class Meta:
        model = transaction_models.ProductTransaction
        fields = (
            "updated_after",
            "created_after",
            "updated_before",
            "only_quantity_available",
            "skip_only_connect",
            "entity",
        )
    
    def get_filter_query(self, filter_type, entity, user):
        """
        Returns the appropriate query filter based on filter_type.
        """
        filter_map = {
            'user': (
                Q(source=entity, creator=user) | 
                Q(destination=entity, creator=user)
            ),
            'all': Q(source=entity) | Q(destination=entity)
        }
        return filter_map.get(filter_type, Q())

    @property
    def qs(self):
        """Return filtered queryset."""
        parent_queryset = super().qs

        # If the current user is an admin, return the unfiltered queryset
        current_user = auth_utils.get_current_user()
        if current_user.is_admin:
            return parent_queryset

        entity = auth_utils.get_current_entity()
        filter_type = self.request.query_params.get('filter_by', 'user')
        
        # Get the appropriate filter and apply it
        filter_query = self.get_filter_query(filter_type, entity, current_user)
        return parent_queryset.filter(filter_query)


    def skip_only_connect_filter(self, queryset, name, value):
        """Return queryset."""
        if value:
            return queryset.filter(
                Q(source__only_connect=False) & Q(destination__only_connect=False)
            )
        return queryset

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

    def entity_filter(self, queryset, name, value):
        """Return queryset."""
        entity = Entity.objects.filter(id=decode(value)).first()
        return queryset.filter(Q(source=entity) | Q(destination=entity))


class PaymentTransactionFilterSet(filters.FilterSet):
    """A filter set for the Farmer model.

    This filter set allows filtering of Payment Transaction objects.
    """

    updated_after = filters.NumberFilter(
        method="updated_after_filter", field_name="updated_on"
    )
    created_after = filters.NumberFilter(
        method="updated_after_filter", field_name="created_on"
    )
    updated_before = filters.NumberFilter(
        method="updated_before_filter", field_name="updated_on"
    )

    class Meta:
        model = payment_models.PaymentTransaction
        fields = ["payment_type"]
        fields = (
            "payment_type",
            "updated_after",
            "created_after",
            "updated_before",
        )

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
