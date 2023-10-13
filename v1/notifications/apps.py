from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'v1.notifications'

    def ready(self):
        from .manager import validate_notifications
        validate_notifications()

