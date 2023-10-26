from django.db import models
from django.utils.translation import gettext_lazy as _

from . import constants as from_consts
from base.db.models import AbstractBaseModel


class ReferenceForm(AbstractBaseModel):
    """
    Model representing a reference form.

    Attributes:
        owner (Company): The company that owns the reference form.
        form_type (str): The type of the reference form.
    """

    owner = models.ForeignKey(
        "supply_chains.Company",
        related_name="reference_forms",
        on_delete=models.CASCADE,
        verbose_name=_("Owner"),
    )
    form_type = models.CharField(
        max_length=20,
        choices=from_consts.FormType.choices,
        verbose_name=_("Form Type"),
    )

    def __str__(self):
        return f"{self.owner} - {self.form_type}"


class ReferenceFormField(AbstractBaseModel):
    """
    Model representing a field within a reference form.

    Attributes:
        reference_form (ReferenceForm): The reference form to which this field
            belongs.
        label (str): The label or name of the form field.
        type (str): The type of the field.
        required (bool): Indicates whether the field is required.
    """

    reference_form = models.ForeignKey(
        ReferenceForm,
        related_name="fields",
        on_delete=models.CASCADE,
        verbose_name=_("Form"),
    )
    label = models.CharField(max_length=100, verbose_name=_("Label"))
    type = models.CharField(
        max_length=20,
        choices=from_consts.FormFieldType.choices,
        verbose_name=_("Field Type"),
    )
    required = models.BooleanField(default=True, verbose_name=_("Required"))

    def __str__(self):
        return f"{self.form} - {self.label}"


class Form(AbstractBaseModel):
    """
    Model representing a specific form instance.

    Attributes:
        reference (ReferenceForm): The reference form associated with this
        instance.
    """

    reference = models.ForeignKey(
        ReferenceForm,
        related_name="forms",
        on_delete=models.CASCADE,
        verbose_name=_("Reference"),
    )

    def __str__(self):
        return f"{self.reference}"


class FormValues(AbstractBaseModel):
    """
    Model representing values associated with form fields within a specific
    form instance.

    Attributes:
        form (Form): The specific form instance.
        field (ReferenceFormField): The form field.
        value (str): The actual value for the form field.
    """

    form = models.ForeignKey(
        Form,
        related_name="values",
        on_delete=models.CASCADE,
        verbose_name=_("Form"),
    )
    field = models.ForeignKey(
        ReferenceFormField,
        related_name="values",
        on_delete=models.CASCADE,
        verbose_name=_("Field"),
    )
    value = models.CharField(max_length=100, verbose_name=_("Value"))

    class Meta:
        unique_together = ("form", "field")

    def __str__(self):
        return f"{self.form} - {self.field} - {self.value}"
