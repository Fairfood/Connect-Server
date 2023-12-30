"""URLs of the notifications."""
from django.urls import path

from . import views

urlpatterns = [
    # Notifications APIs
    path(
        "summary/",
        views.NotificationSummaryView.as_view(),
        name="notification_summary",
    ),
    path(
        "read/",
        views.NotificationReadView.as_view(),
        name="read_notifications",
    ),
    path("", views.NotificationsListView.as_view(), name="list_notification"),
]
