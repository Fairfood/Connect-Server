"""Constants under the notifications section are stored here."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class NotificationCondition(models.IntegerChoices):
    ENABLED = 101, _('Enabled')
    DISABLED = 111, _('Disabled')
    IF_USER_ACTIVE = 121, _('If user is active')
