from django.contrib import admin

from base.db.admin import ReadOnlyAdmin

# Register your models here.

from . import models


@admin.register(models.Notification)
class NotificationAdmin(ReadOnlyAdmin):
    pass

@admin.register(models.SMSAlerts)
class SMSAlertsAdmin(ReadOnlyAdmin):
    list_display = ('phone', 'message')
