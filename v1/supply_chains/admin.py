"""Models are registered with django admin at here."""
from django.contrib import admin

from .models import company_models
from base.db.admin import BaseAdmin


class CompanyAdmin(BaseAdmin):
    """
    Model representing a company entity.
    """

    list_display = (
        "name",
        "id",
    )
    search_fields = ["name"]


class CompanyMemberAdmin(BaseAdmin):
    """
    Model representing a company member entity.
    """

    list_display = (
        "company",
        "id",
    )
    search_fields = ["company"]


admin.site.register(company_models.Company, CompanyAdmin)
admin.site.register(company_models.CompanyMember, CompanyMemberAdmin)
