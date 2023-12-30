from django.apps import AppConfig


class FormsConfig(AppConfig):
    """Configuration class for the 'forms' app.

    This class defines the configuration for the 'forms' app, specifying
    the default auto field and the app's name.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "v1.forms"
