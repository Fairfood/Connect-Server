"""APIs for Notifications."""
from django.conf import settings
from django.db.models import Count
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters
from rest_framework import generics
from rest_framework import views
from rest_framework.response import Response

from base import exceptions
from base.authentication import session
from utilities.functions import encode
from v1.notifications import filters as noti_filters
from v1.notifications import serializers
from v1.notifications.models import Notification

# Create your views here.


class NotificationSummaryView(views.APIView):
    """API view to retrieve notification summary.

    This view provides an API endpoint to retrieve a summary of
    notifications for a user, including counts of notifications and
    unread notifications per entity.
    """

    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        """Get the summary of notifications."""
        notif_summary = (
            Notification.objects.filter(
                user_id=session.get_from_local("user_id"), visibility=True
            )
            .values(
                "target_entity", "target_entity__name", "target_entity__image"
            )
            .annotate(
                count=Count("id"),
                unread_count=Count("id", filter=Q(is_read=False)),
            )
            .order_by("-count")
        )

        notification_data = []
        for notif in notif_summary:
            notification_data.append(
                {
                    "count": notif["count"],
                    "unread_count": notif["unread_count"],
                    "entity": {
                        "id": encode(notif["target_entity"]),
                        "name": notif["target_entity__name"],
                        "image": (
                            f"https:{settings.MEDIA_URL}"
                            f"{notif['target_entity__image']}"
                        )
                        if notif["target_entity__image"]
                        else "",
                    },
                }
            )
        return Response(notification_data)


class NotificationsListView(generics.ListAPIView):
    """API to list notifications with option to filter by entity."""

    serializer_class = serializers.NotificationSerializer
    filterset_class = noti_filters.NotificationFilter
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["title", "body"]

    def get_queryset(self):
        """Get the queryset of notifications.

        This method returns a queryset of notifications filtered by user
        ID and visibility. It uses the user ID retrieved from the
        session and includes related entities (actor, target, and
        creator) through select_related for optimization.
        """

        return Notification.objects.filter(
            user_id=session.get_from_local("user_id"), visibility=True
        ).select_related("actor_entity", "target_entity", "creator")


class NotificationReadView(views.APIView):
    """API view for marking notifications as read.

    This view provides an API endpoint to mark notifications as read.
    Only supports the HTTP PATCH method.
    """

    http_method_names = ["patch"]

    @swagger_auto_schema(request_body=serializers.ReadNotificationSerializer)
    def patch(self, request, *args, **kwargs):
        """Mark notifications as read."""
        notification_serializer = serializers.ReadNotificationSerializer(
            data=request.data
        )
        if notification_serializer.is_valid():
            notification_serializer.save()
            return Response(notification_serializer.data)
        raise exceptions.BadRequest(notification_serializer.errors)
