from django.apps import AppConfig


class AuthConfig(AppConfig):
    """Configuration class for the 'apiauth' app.

    This class defines the configuration for the 'apiauth' app,
    specifying the default auto field and the app's name.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "v1.apiauth"
