from django.apps import AppConfig


class CatalogsConfig(AppConfig):
    """Configuration class for the 'catalogs' app.

    This class defines the configuration for the 'catalogs' app,
    specifying the default auto field and the app's name.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "v1.catalogs"
