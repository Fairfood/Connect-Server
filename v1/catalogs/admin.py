"""Models are registered with django admin at here."""
from django.contrib import admin

from .models import common_models
from .models import product_models
from base.db.admin import BaseAdmin


class CurrencyAdmin(BaseAdmin):
    """Admin class for Currency model."""

    list_display = (
        "name",
        "code",
        "id",
    )
    search_fields = ["name"]


class ProductAdmin(BaseAdmin):
    """Product admin class."""

    list_display = (
        "name",
        "id",
    )
    search_fields = ["name"]


class ConnectCardAdmin(BaseAdmin):
    """ConnectCard admin class."""

    list_display = (
        "id",
        "display_id",
        "card_id",
        "is_active"
    )
    search_fields = ["display_id", "display_id"]


class PremiumOptionTabularInline(admin.TabularInline):
    """Tabular inline admin class for PremiumOption model.

    This class is used to display PremiumOption objects in a tabular
    format within the Django admin.
    """

    model = product_models.PremiumOption
    extra = 0


class PremiumRangeTabularInline(admin.TabularInline):
    """A tabular inline admin class for the PremiumRange model."""

    model = product_models.PremiumRange
    extra = 0


class PremiumAdmin(BaseAdmin):
    """Admin class for Premium model.

    This class provides the admin class for Premium model.
    """

    list_display = (
        "name",
        "owner",
        "id",
    )
    inlines = [PremiumOptionTabularInline, PremiumRangeTabularInline]
    search_fields = ["name", "owner"]


admin.site.register(common_models.Currency, CurrencyAdmin)
admin.site.register(product_models.Product, ProductAdmin)
admin.site.register(product_models.Premium, PremiumAdmin)
admin.site.register(product_models.ConnectCard, ConnectCardAdmin)
