# from django.contrib import admin
# Register your models here.
from django.contrib.admin import TabularInline

from base.db import admin
from v1.forms.models import FormValues
from v1.forms.serializers import ReferenceFormFieldSerializer


class ReferenceFormFieldTabularInline(TabularInline):
    """
    A tabular inline form for editing reference form fields in the admin
    interface.

    This class is used to define a tabular inline form for editing reference
    form fields in the admin interface. It inherits from Django's built-in
    `TabularInline` class and uses the `ReferenceFormFieldSerializer` model
    to define the fields that can be edited.

    """

    model = ReferenceFormFieldSerializer
    extra = 0


class ReferenceFormAdmin(admin.BaseAdmin):
    """
    Admin interface for managing reference forms.

    This class defines the behavior of the admin interface for managing
    reference forms. It specifies the fields to be
    displayed in the list view, as well as the fields that can be searched.
    """

    list_display = (
        "owner",
        "id",
    )
    inlines = [ReferenceFormFieldTabularInline]


class FormValueTabularInline(TabularInline):
    """
    A tabular inline form for editing form values in the admin interface.

    This class is used to define a tabular inline form for editing form values
    in the admin interface. It inherits from Django's built-in `TabularInline`
    class and uses the `FormValuesSerializer` model to define the fields that
    can be edited.
    """

    model = FormValues
    extra = 0


class FormAdmin(admin.BaseAdmin):
    """
    Admin interface for managing forms.

    This class defines the behavior of the admin interface for managing forms.
    It specifies the fields to be displayed in the list view, as well as the
    fields that can be searched.
    """

    list_display = (
        "reference",
        "type",
        "id",
    )
    inlines = [FormValueTabularInline]
