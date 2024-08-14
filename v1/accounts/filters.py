from django_filters import rest_framework as filters
from django.db.models import Q
from v1.accounts import models as user_models


class UserFilter(filters.FilterSet):
    """Filter for CustomUser"""

    email = filters.CharFilter(method="filter_email")

    class Meta:
        model = user_models.CustomUser
        fields = ["email", ]

    def filter_email(self, queryset, name, value):
        """To perform function to filter by email."""
        query = Q(email=value)
        return queryset.filter(query)
