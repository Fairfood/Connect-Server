from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """Configuration class for the 'notifications' app.

    This class defines the configuration for the 'notifications' app,
    specifying the default auto field, the app's name, and includes a
    'ready' method for initialization tasks, such as validating
    notifications.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "v1.notifications"

    def ready(self):
        """Initialization method for the 'notifications' app.

        Performs tasks that need to be executed when the app is ready,
        such as validating notifications.
        """
        from .manager import validate_notifications

        validate_notifications()
