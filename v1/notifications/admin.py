from django.contrib import admin

from . import models
from base.db.admin import ReadOnlyAdmin

# Register your models here.


@admin.register(models.Notification)
class NotificationAdmin(ReadOnlyAdmin):
    pass


@admin.register(models.SMSAlerts)
class SMSAlertsAdmin(ReadOnlyAdmin):
    list_display = ("phone", "message")
