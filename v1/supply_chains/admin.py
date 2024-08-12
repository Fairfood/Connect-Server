"""Models are registered with django admin at here."""
from django.contrib import admin

from base.db.admin import BaseAdmin

from .models import base_models, company_models, farmer_models


class CompanyProductInline(admin.TabularInline):
    """Admin class for Company model."""

    model = company_models.CompanyProduct
    extra = 0


class CompanyAdmin(BaseAdmin):
    """Model representing a company entity."""

    list_display = (
        "name",
        "id",
    )
    search_fields = ["name"]
    inlines = [CompanyProductInline]


class CompanyMemberAdmin(BaseAdmin):
    """Model representing a company member entity."""

    list_display = (
        "company",
        "user",
        "id",
    )
    search_fields = ["company"]


class EntityCardAdmin(BaseAdmin):
    """Model representing a company member entity."""

    list_display = (
        "id",
        "card",
        "entity",
        "is_active"
    )
    search_fields = ['id','card__card_id', 'card__display_id','entity__name']


class FarmerAdmin(BaseAdmin):
    """Model representing a company entity."""

    list_display = ("first_name", "last_name", "id", "buyer")
    search_fields = ["first_name", "last_name"]


admin.site.register(company_models.Company, CompanyAdmin)
admin.site.register(company_models.CompanyMember, CompanyMemberAdmin)
admin.site.register(farmer_models.Farmer, FarmerAdmin)
admin.site.register(base_models.EntityCard, EntityCardAdmin)
