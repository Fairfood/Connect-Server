from django.apps import AppConfig


class SupplyChainsConfig(AppConfig):
    """Configuration class for the 'supply_chains' app.

    This class defines the configuration for the 'supply_chains' app,
    specifying the default auto field and the app's name.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "v1.supply_chains"
