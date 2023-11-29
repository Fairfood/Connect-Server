"""Models are registered with django admin at here."""
from django.contrib import admin

from .models import common_models
from .models import product_models
from base.db.admin import BaseAdmin


class CountryAdmin(BaseAdmin):
    list_display = (
        "name",
        "alpha_2",
        "dial_code",
        "latitude",
        "longitude",
        "id",
    )
    search_fields = [
        "name",
        "code",
        "dial_code",
    ]


class ProvinceAdmin(BaseAdmin):
    list_display = (
        "country",
        "name",
        "latitude",
        "longitude",
        "id",
    )
    search_fields = ["name"]


class CurrencyAdmin(BaseAdmin):
    list_display = (
        "name",
        "code",
        "id",
    )
    search_fields = ["name"]


class ProductAdmin(BaseAdmin):
    list_display = (
        "name",
        "id",
    )
    search_fields = ["name"]


class ConnectCardAdmin(BaseAdmin):
    list_display = (
        "display_id",
        "id",
    )
    search_fields = ["name"]


class PremiumOptionTabularInline(admin.TabularInline):
    model = product_models.PremiumOption
    extra = 0


class PremiumAdmin(BaseAdmin):
    list_display = (
        "name",
        "id",
    )
    inlines = [
        PremiumOptionTabularInline,
    ]
    search_fields = ["name"]


admin.site.register(common_models.Country, CountryAdmin)
admin.site.register(common_models.Province, ProvinceAdmin)
admin.site.register(common_models.Currency, CurrencyAdmin)
admin.site.register(product_models.Product, ProductAdmin)
admin.site.register(product_models.Premium, PremiumAdmin)
admin.site.register(product_models.ConnectCard, ConnectCardAdmin)
