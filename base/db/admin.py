from django.contrib import admin
from django.contrib.postgres import fields
from django_extensions.db.fields import json
from django_json_widget.widgets import JSONEditorWidget


class BaseAdmin(admin.ModelAdmin):
    readonly_fields = ("id", "created_on", "updated_on", "creator", "updater")

    search_fields = ["id"]

    list_display = ("__str__", "id")

    formfield_overrides = {
        json.JSONField: {"widget": JSONEditorWidget},
        fields.JSONField: {"widget": JSONEditorWidget},
    }

    def save_model(self, request, obj, form, change):
        # adding the entry for the first time
        if not change:
            obj.creator = request.user
            obj.updater = request.user

        # updating already existing record
        else:
            obj.updater = request.user
        obj.save()

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        queryset |= self.model.objects.filter(id=search_term)
        return queryset, use_distinct


class ReadOnlyAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        return list(
            set(
                [field.name for field in self.opts.local_fields]
                + [field.name for field in self.opts.local_many_to_many]
            )
        )

    list_display = ("__str__", "id")
