from django.contrib import admin
from django.contrib.postgres import fields
from django_extensions.db.fields import json
from django_json_widget.widgets import JSONEditorWidget


class BaseAdmin(admin.ModelAdmin):
    """Base admin class for all models.

    This class provides the base admin class for all models, providing
    common fields and methods.
    """

    readonly_fields = ("id", "created_on", "updated_on", "creator", "updater")

    search_fields = ["id"]

    list_display = ("__str__", "id")

    formfield_overrides = {
        json.JSONField: {"widget": JSONEditorWidget},
        fields.JSONField: {"widget": JSONEditorWidget},
    }

    def save_model(self, request, obj, form, change):
        """Override save method to add creator and updater."""
        # adding the entry for the first time
        if not change:
            obj.creator = request.user
            obj.updater = request.user

        # updating already existing record
        else:
            obj.updater = request.user
        obj.save()

    def get_search_results(self, request, queryset, search_term):
        """Override search method to search by id."""
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        queryset |= self.model.objects.filter(id=search_term)
        return queryset, use_distinct


class ReadOnlyAdmin(admin.ModelAdmin):
    """Admin class for creating read-only views in the Django admin.

    This class provides a read-only view for Django admin by setting all
    fields to be read-only.
    """

    def get_readonly_fields(self, request, obj=None):
        """Get the list of read-only fields.

        Returns:
            list: List of field names that should be read-only.
        """
        return list(
            set(
                [field.name for field in self.opts.local_fields]
                + [field.name for field in self.opts.local_many_to_many]
            )
        )

    list_display = ("__str__", "id")
