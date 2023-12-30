from django.contrib import admin

from base.db.admin import BaseAdmin
from v1.transactions.models.transaction_models import ProductTransaction


@admin.register(ProductTransaction)
class ProductTransactionAdmin(BaseAdmin):
    """Admin class for managing ProductTransaction instances.

    Attributes:
    - list_display (list): The fields to display in the admin list view.
    - inlines (list): Specifies the inlines to be used with this admin class.
    """

    list_display = ["id", "source", "destination"]
    readonly_fields = ["parents"]
