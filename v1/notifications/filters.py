"""Filters used in the app accounts."""
from django_filters import rest_framework as filters

from v1.notifications.models import Notification


class NotificationFilter(filters.FilterSet):
    """Filter for Notifications."""

    entity = filters.CharFilter(field_name="target_entity")
    is_read = filters.BooleanFilter()

    class Meta:
        model = Notification
        fields = ["entity", "is_read"]
