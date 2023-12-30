from django.contrib import admin

from .models import Form
from .models import FormField
from .models import FormFieldConfig
from .models import Submission
from .models import SubmissionValues
from base.db.admin import BaseAdmin


class FormFieldInline(admin.TabularInline):
    """Inline form for FormField within the Form admin page.

    Attributes:
    - model (model): The model being represented in this inline form.
    - extra (int): The number of empty forms to display.
    - fields (list): The fields to display in the inline form.
    - fk_name (str): The name of the foreign key field that relates to the
        parent form.
    """

    model = FormField
    extra = 0
    fields = [
        "label",
        "type",
        "required",
        "key",
        "default_value",
        "options",
    ]
    fk_name = "form"


class FormFieldConfigInline(admin.TabularInline):
    """Inline form for Form Field Conguration within the Form admin page.

    Attributes:
    - model (model): The model being represented in this inline form.
    - extra (int): The number of empty forms to display.
    - fields (list): The fields to display in the inline form.
    - fk_name (str): The name of the foreign key field that relates to the
        parent form.
    """

    model = FormFieldConfig
    extra = 0
    fields = ["label", "required", "key", "visibility"]
    fk_name = "form"


@admin.register(Form)
class FormAdmin(BaseAdmin):
    """Admin class for managing Form instances.

    Attributes:
    - list_display (list): The fields to display in the admin list view.
    - inlines (list): Specifies the inlines to be used with this admin class.
    """

    list_display = ["id", "owner", "form_type"]
    inlines = [FormFieldInline, FormFieldConfigInline]


class SubmissionValuesInline(admin.TabularInline):
    """Inline form for SubmissionValues within the Submission admin page.

    Attributes:
    - model (model): The model being represented in this inline form.
    - extra (int): The number of empty forms to display.
    - fields (list): The fields to display in the inline form.
    - fk_name (str): The name of the foreign key field that relates to the
        parent form.
    """

    model = SubmissionValues
    extra = 0
    fields = ["field", "value"]
    fk_name = "submission"


@admin.register(Submission)
class SubmissionAdmin(BaseAdmin):
    """Admin class for managing Submission instances.

    Attributes:
    - list_display (list): The fields to display in the admin list view.
    - inlines (list): Specifies the inlines to be used with this admin class.
    """

    list_display = ["id", "form"]
    inlines = [SubmissionValuesInline]
