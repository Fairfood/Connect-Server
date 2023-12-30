from django.contrib import admin

from . import models
from base.db.admin import ReadOnlyAdmin

# Register your models here.


@admin.register(models.Notification)
class NotificationAdmin(ReadOnlyAdmin):
    """Admin class for the Notification model.

    This class customizes the admin interface for managing Notification
    instances.

    It inherits from ReadOnlyAdmin to provide read-only access.
    """

    pass


@admin.register(models.SMSAlerts)
class SMSAlertsAdmin(ReadOnlyAdmin):
    """Admin class for the SMSAlerts model.

    This class customizes the admin interface for managing SMSAlerts
    instances. It inherits from ReadOnlyAdmin and specifies the list
    display fields as `phone` and `message`.
    """

    list_display = ("phone", "message")
