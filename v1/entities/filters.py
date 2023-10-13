"""Filters used in the country api."""

from django_filters import rest_framework as filters

from django.db.models import Q

from base.authentication import utilities as auth_utils

from base.authentication import session

from v1.entities import constants as entity_constants
from v1.entities import models as entity_models


class EntityMemberFilter(filters.FilterSet):
    """
    Filterclass for country-list api.
    """
    email = filters.CharFilter(method='email_filter')

    class Meta:
        """
        Meta Info.
        """
        model = entity_models.EntityMember
        fields = ('email', )

    def email_filter(self, queryset, name, value):
        """
        Search filter on the basis of country name.
        """
        query = Q(user__email=value)
        return queryset.filter(query)


class EntityFilter(filters.FilterSet):
    """
    Filter to filter entities
    """

    type = filters.ChoiceFilter(choices=entity_constants.EntityType.choices)
    status = filters.ChoiceFilter(choices=entity_constants.EntityStatus.choices)
    include_current_entity = filters.BooleanFilter(method='filter_current_entity')

    class Meta:
        model = entity_models.Entity
        fields = ['type', 'status',]
    
    def filter_current_entity(self, queryset, name, value):
        if value == True:
            current_entity = auth_utils.get_current_entity()
            queryset |= entity_models.Entity.objects.filter(
                id=current_entity.id).distinct('id')
        return queryset
