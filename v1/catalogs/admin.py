"""Models are registered with django admin at here."""
from django.contrib import admin

from base.db.admin import BaseAdmin
from v1.catalogs.models import common_models as catalog_models


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


admin.site.register(catalog_models.Country, CountryAdmin)
admin.site.register(catalog_models.Province, ProvinceAdmin)
admin.site.register(catalog_models.Currency, CurrencyAdmin)
