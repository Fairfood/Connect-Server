from django_filters import rest_framework as filters

from base.authentication import utilities as utils
from utilities.functions import unix_to_datetime
from v1.supply_chains.models.base_models import EntityCard
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

    class Meta:
        model = Farmer
        fields = {
            "first_name": ["icontains"],
            "last_name": ["icontains"],
            "number": ["icontains"],
        }

    @property
    def qs(self):
        """Return queryset."""
        parent = super().qs.distinct("id")
        user = utils.get_current_user()
        if user.is_admin:
            return parent

        entity = utils.get_current_entity()
        return parent.filter(buyer=entity)

    def after_date_time_filter(self, queryset, name, value):
        """Return queryset."""
        name += "__gt"
        value = unix_to_datetime(value)
        return queryset.filter(**{name: value})


class EntityCardFilterSet(filters.FilterSet):
    """A filter set for the EntityCard model.

    This filter set allows filtering of EntityCard objects.
    """

    card_id = filters.CharFilter(
        field_name="card__card_id", lookup_expr="icontains"
    )
    created_after = filters.NumberFilter(
        method="after_date_time_filter", field_name="updated_on"
    )

    class Meta:
        model = EntityCard
        fields = ("card_id",)

    @property
    def qs(self):
        """Return queryset."""
        parent = super().qs
        user = utils.get_current_user()
        if user.is_admin:
            return parent
        entity = utils.get_current_entity()
        return parent.filter(entity=entity)

    def after_date_time_filter(self, queryset, name, value):
        """Return queryset."""
        name += "__gt"
        value = unix_to_datetime(value)
        return queryset.filter(**{name: value})
