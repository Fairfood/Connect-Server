from django.contrib import admin

from base.db.admin import BaseAdmin
from v1.transactions.models.payment_models import PaymentTransaction
from v1.transactions.models.transaction_models import ProductTransaction


@admin.register(ProductTransaction)
class ProductTransactionAdmin(BaseAdmin):
    """Admin class for managing ProductTransaction instances.

    Attributes:
    - list_display (list): The fields to display in the admin list view.
    - inlines (list): Specifies the inlines to be used with this admin class.
    """

    list_display = [
        "id",
        "source",
        "destination",
        "date",
        "quantity",
        "creator_email",
    ]
    autocomplete_fields = ['product', "source", "destination", "card","parents",]

    def creator_email(self, obj):
        """Get creator."""
        return obj.creator.email


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(BaseAdmin):
    """Admin class for managing ProductTransaction instances.

    Attributes:
    - list_display (list): The fields to display in the admin list view.
    - inlines (list): Specifies the inlines to be used with this admin class.
    """

    list_display = [
        "id",
        "source",
        "destination",
        "date",
        "amount",
        "creator_email",
        "premium_name",
    ]
    autocomplete_fields = ['premium', "currency", "transaction", "source", "destination", "card",]

    def creator_email(self, obj):
        """Get creator."""
        return obj.creator.email

    def premium_name(self, obj):
        """Get premium name."""
        return obj.premium.name if obj.premium else ""
