"""Models are registered with django admin at here."""

from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from base.db.admin import BaseAdmin

from .models import base_models, company_models, farmer_models


class FarmerBuyerListFilter(admin.SimpleListFilter):
    title = _("Buyer")
    # Parameter for the filter that will be used in the URL query.
    parameter_name = "buyer"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            model_admin.model.objects.values_list("buyer__id", "buyer__company__name")
            .distinct("buyer__id")
            .order_by("-buyer__id")
            .all()[:10]
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(buyer=self.value())


class FarmerCreatorListFilter(admin.SimpleListFilter):
    title = _("Creator")
    parameter_name = "creator"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        creators = (
            model_admin.model.objects.filter(creator__id__isnull=False)
            .values_list("creator__id", "creator__first_name", "creator__last_name")
            .distinct("creator__id")
            .order_by("-creator__id")
            .all()[:10]
        )

        return [(creator[0], creator[1] + " " + creator[2]) for creator in creators]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(creator=self.value())


class CompanyProductInline(admin.TabularInline):
    """Admin class for Company model."""

    model = company_models.CompanyProduct
    extra = 0


class CompanyAdmin(BaseAdmin):
    """Model representing a company entity."""

    list_display = (
        "name",
        "id",
        "created_on"
    )
    search_fields = ["name"]
    readonly_fields = (
        "created_on",
        "updated_on",
        "creator",
        "updater",
    )
    autocomplete_fields = ['buyer', "currency", "entity_card",]
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

    list_display = ("id", "card", "entity", "is_active")
    search_fields = ["id", "card__card_id", "card__display_id"]


class FarmerAdmin(BaseAdmin):
    """Model representing a company entity."""

    list_display = (
        "id",
        "first_name",
        "last_name",
        "province",
        "country",
        "buyer",
        "creator",
        "created_on"
    )
    search_fields = ["first_name", "last_name", "id"]
    autocomplete_fields = ['buyer', "submission", "entity_card",]
    list_filter = [
        FarmerBuyerListFilter,
        FarmerCreatorListFilter,
    ]


class EntityAdmin(BaseAdmin):
    """Model representing a company entity."""

    list_display = ("id", "only_connect", "buyer")


class ExternalServiceAdminForm(forms.ModelForm):
    def clean_service_url(self):
        if "{{refernce_id}}" not in self.cleaned_data["service_url"]:
            raise forms.ValidationError("The service url should contain a {{refernce_id}} text.")
        return self.cleaned_data["service_url"]



class ExternalServiceAdmin(BaseAdmin):
    """Model representing a external service entity."""

    form = ExternalServiceAdminForm
    list_display = ("id", "name", "is_available")
    readonly_fields = (
        "created_on",
        "updated_on",
        "creator",
        "updater",
    )


class FarmerServiceAdmin(BaseAdmin):
    """Model representing a farmer service entity."""

    list_display = ("id", "farmer", "service", "refernce_id", "is_active", "updated_on")
    autocomplete_fields = ['farmer',]
    readonly_fields = (
        "created_on",
        "updated_on",
        "creator",
        "updater",
    )


admin.site.register(company_models.Company, CompanyAdmin)
admin.site.register(company_models.CompanyMember, CompanyMemberAdmin)
admin.site.register(farmer_models.Farmer, FarmerAdmin)
admin.site.register(base_models.EntityCard, EntityCardAdmin)
admin.site.register(base_models.Entity, EntityAdmin)
admin.site.register(farmer_models.ExternalService, ExternalServiceAdmin)
admin.site.register(farmer_models.FarmerService, FarmerServiceAdmin)

