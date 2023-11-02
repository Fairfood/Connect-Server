from django_filters import rest_framework as filters

from base.authentication import utilities as utils
from v1.supply_chains.models.base_models import EntityCard
from v1.supply_chains.models.farmer_models import Farmer


class FarmerFilterSet(filters.FilterSet):
    """
    A filter set for the Farmer model.

    This filter set allows filtering of Farmer objects.
    """

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
        parent = super().qs
        entity = utils.get_current_entity()
        return parent.filter(buyer=entity)


class EntityCardFilterSet(filters.FilterSet):
    """
    A filter set for the EntityCard model.

    This filter set allows filtering of EntityCard objects.
    """

    card_id = filters.CharFilter(
        field_name="card__card_id", lookup_expr="icontains"
    )

    class Meta:
        model = EntityCard
        fields = ("card_id",)

    @property
    def qs(self):
        """Return queryset."""
        parent = super().qs
        entity = utils.get_current_entity()
        return parent.filter(entity=entity)
