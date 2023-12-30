"""Constants under the notifications section are stored here."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class NotificationCondition(models.IntegerChoices):
    """Enumeration of notification conditions.

    Represents different conditions for enabling or disabling notifications
    within the application.

    Attributes:
        ENABLED (int): Indicates that the notification is enabled.
        DISABLED (int): Indicates that the notification is disabled.
        IF_USER_ACTIVE (int): Indicates that the notification is enabled only
                              if the user is active.
    """

    ENABLED = 101, _("Enabled")
    DISABLED = 111, _("Disabled")
    IF_USER_ACTIVE = 121, _("If user is active")
