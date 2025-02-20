from django.db.models import Q
from django_filters import rest_framework as filters

from base.authentication import utilities as utils
from utilities.functions import decode, unix_to_datetime
from v1.supply_chains.models.base_models import EntityBuyer, EntityCard
from v1.supply_chains.models.company_models import Company
from v1.supply_chains.models.farmer_models import Farmer


class FarmerFilterSet(filters.FilterSet):
    """A filter set for the Farmer model.

    This filter set allows filtering of Farmer objects.
    """

    updated_after = filters.NumberFilter(
        method="after_date_time_filter", field_name="updated_on"
    )
    created_after = filters.NumberFilter(
        method="after_date_time_filter", field_name="created_on"
    )
    created_after_farmer = filters.CharFilter(
        method="after_farmer_id_filter", field_name="id"
    )
    skip_only_connect = filters.BooleanFilter(method="skip_only_connect_filter")
    first_name = filters.CharFilter(lookup_expr="icontains")
    last_name = filters.CharFilter(lookup_expr="icontains")
    number = filters.CharFilter(lookup_expr="icontains")
    entity = filters.CharFilter(method="entity_filter")

    class Meta:
        model = Farmer
        fields = (
            "first_name",
            "last_name",
            "number",
            "updated_after",
            "created_after",
            "skip_only_connect",
            "reference_number",
            "created_after_farmer",
            "entity"
        )

    @property
    def qs(self):
        """Return queryset."""
        parent = super().qs.distinct("id")
        user = utils.get_current_user()
        if user.is_admin:
            return parent

        entity = utils.get_current_entity()
        return parent.filter(
                id__in=EntityBuyer.objects.filter(
                    buyer=entity).values_list("entity__id", flat=True)
                ).distinct("id")

    def skip_only_connect_filter(self, queryset, name, value):
        """Return queryset."""
        if value:
            return queryset.filter(
                id__in=EntityBuyer.objects.filter(
                    buyer__only_connect=False).values_list("entity__id", flat=True)
                )
        return queryset

    def after_date_time_filter(self, queryset, name, value):
        """Return queryset."""
        name += "__gt"
        value = unix_to_datetime(value)
        return queryset.filter(**{name: value})

    def after_farmer_id_filter(self, queryset, name, value):
        """Return queryset."""
        return queryset.filter(id__gt= value)

    def entity_filter(self, queryset, name, value):
        """Return queryset."""
        queryset = queryset.filter(
            id__in=EntityBuyer.objects.filter(
                buyer=decode(value)
            ).values_list("entity__id", flat=True)
        ).distinct("id")
        return queryset


class EntityCardFilterSet(filters.FilterSet):
    """A filter set for the EntityCard model.

    This filter set allows filtering of EntityCard objects.
    """

    card_id = filters.CharFilter(field_name="card__card_id", lookup_expr="icontains")
    created_after = filters.NumberFilter(
        method="after_date_time_filter", field_name="created_on"
    )
    updated_after = filters.NumberFilter(
        method="after_date_time_filter", field_name="updated_on"
    )
    skip_only_connect = filters.BooleanFilter(method="skip_only_connect_filter")
    entity = filters.CharFilter(method="entity_filter")

    class Meta:
        model = EntityCard
        fields = (
            "card_id", "created_after", "updated_after", "skip_only_connect", 
            "entity"
        )

    @property
    def qs(self):
        """Return queryset."""
        parent = super().qs
        user = utils.get_current_user()
        if user.is_admin:
            return parent
        entity = utils.get_current_entity()
        return parent.filter(entity=entity)

    def skip_only_connect_filter(self, queryset, name, value):
        """Return queryset."""
        if value:
            queryset = queryset.filter(
                Q(entity__only_connect=False) & Q(entity__entity_buyers__buyer__only_connect=False)
            ).distinct()
        return queryset

    def after_date_time_filter(self, queryset, name, value):
        """Return queryset."""
        name += "__gt"
        value = unix_to_datetime(value)
        return queryset.filter(**{name: value}).order_by('updated_on')

    def entity_filter(self, queryset, name, value):
        """Filter based on entity"""
        decoded_value = decode(value)

        # Get the entity IDs associated with the decoded value, for both 
        # Farmer and Company
        entity_ids = EntityBuyer.objects.filter(
            Q(buyer=decoded_value) | Q(entity=decoded_value)
        ).values_list("entity__id", flat=True).distinct()

        # Filter the queryset using the retrieved entity IDs
        queryset = queryset.filter(
            Q(entity__id__in=entity_ids) & Q(is_active=True)
        )
        return queryset


class OpenFilterTransactions(filters.FilterSet):
    """Filter to filter transactions by updated time."""

    start_date = filters.NumberFilter(method="get_transactions_start_date")
    end_date = filters.NumberFilter(method="get_transactions_end_date")

    def get_transactions_start_date(self, queryset, name, value):
        """Get transactions start_date_date."""
        dt = unix_to_datetime(value)
        return queryset.filter(created_on__gte=dt)

    def get_transactions_end_date(self, queryset, name, value):
        """Get transactions end_date."""
        dt = unix_to_datetime(value)
        return queryset.filter(created_on__lte=dt)
