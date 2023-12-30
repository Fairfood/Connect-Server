from django.apps import AppConfig


class TransactionConfig(AppConfig):
    """Configuration class for the 'transactions' app.

    This class defines the configuration for the 'transactions' app,
    specifying the default auto field and the app's name.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "v1.transactions"
