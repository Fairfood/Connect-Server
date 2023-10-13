"""Models are registered with django admin at here."""

from django.contrib import admin
from django.http import HttpResponseRedirect

from base.db.admin import BaseAdmin

from v1.catalogs import models as catalog_models

class CountryAdmin(BaseAdmin):
    list_display = (
        'name', 'alpha_2', 'dial_code', 'latitude','longitude', 'id',)
    search_fields = ['name', 'code', 'dial_code',]


class ProvinceAdmin(BaseAdmin):
    list_display = (
        'country', 'name', 'latitude','longitude', 'id',)
    search_fields = ['name']


class RegionAdmin(BaseAdmin):
    list_display = (
        'province', 'name', 'id',)
    search_fields = ['name']


class VillageAdmin(BaseAdmin):
    list_display = (
        'region', 'name', 'id',)
    search_fields = ['name']


class CurrencyAdmin(BaseAdmin):
    list_display = (
        'name', 'code', 'id',)
    search_fields = ['name']


class CategoryAdmin(BaseAdmin):
    list_display = (
        'name', 'id',)
    search_fields = ['name']
    list_filter = ('type',)


admin.site.register(catalog_models.Country, CountryAdmin)
admin.site.register(catalog_models.Province, ProvinceAdmin)
admin.site.register(catalog_models.Currency, CurrencyAdmin)
admin.site.register(catalog_models.Category, CategoryAdmin)
admin.site.register(catalog_models.Region, RegionAdmin)
admin.site.register(catalog_models.Village, VillageAdmin)
