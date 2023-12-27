from django.db import models
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields.json import JSONField

from . import constants as from_consts
from base.db.models import AbstractBaseModel
from v1.catalogs.models.product_models import Product


class Form(AbstractBaseModel):
    """Represents a Form related to a Company in a supply chain.

    Attributes:
    - owner (models.ForeignKey): The Company that owns this Form.
    - form_type (models.CharField): The type of the Form.

    Related Names:
    - reference_forms: A reverse relation to access Forms owned by a Company.

    Note:
    This model extends AbstractBaseModel.
    """

    owner = models.ForeignKey(
        "supply_chains.Company",
        related_name="forms",
        on_delete=models.CASCADE,
        verbose_name=_("Owner"),
    )
    form_type = models.CharField(
        max_length=20,
        choices=from_consts.FormType.choices,
        default=from_consts.FormType.TRANSACTION,
        verbose_name=_("Form Type"),
    )

    def __str__(self):
        return f"{self.owner} - {self.form_type}"

    @property
    def products(self):
        """Get the associated product for this form.

        If the Form has an associated `company_product`, it returns the product
        associated with it. Otherwise, it returns None.

        Returns:
        product: The associated product or None if not available.
        """
        if hasattr(self, "company_products"):
            return Product.objects.filter(
                id__in=self.company_products.values_list("product", flat=True)
            )
        return Product.objects.none()


class FormField(AbstractBaseModel):
    """Represents a field within a Form.

    Attributes:
    - form (models.ForeignKey): The Form to which this field belongs.
    - label (models.CharField): The label for this field.
    - type (models.CharField): The type of the field.
    - required (models.BooleanField): Indicates whether the field is required.
    - key (models.CharField): The key for this field.

    Related Names:
    - fields: A reverse relation to access fields associated with a Form.
    """

    form = models.ForeignKey(
        Form,
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
    key = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("Key"),
    )
    required = models.BooleanField(default=True, verbose_name=_("Required"))
    default_value = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("Default Value"),
    )
    options = JSONField(
        null=True,
        blank=True,
        verbose_name=_("Options"),
    )

    def __str__(self):
        return f"{self.form} - {self.label}"


class FormFieldConfig(AbstractBaseModel):
    """Represents a field within a Form or a Model.

    Attributes:
    - form (models.ForeignKey): The Form to which this field belongs.
    - label (models.CharField): The label for this field.
    - key (models.CharField): The key for this field.
    - visibility (models.BooleanField): Indicates whether the field is visible.
    - required (models.BooleanField): Indicates whether the field is required.
    """

    form = models.ForeignKey(
        Form,
        related_name="field_config",
        on_delete=models.CASCADE,
        verbose_name=_("Form"),
    )
    label = models.CharField(max_length=100, verbose_name=_("Label"))
    key = models.CharField(max_length=100, verbose_name=_("Key"))
    visibility = models.BooleanField(
        default=True, verbose_name=_("Visibility")
    )
    required = models.BooleanField(default=False, verbose_name=_("Required"))

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["form", "key"], name="unique_form_field_config"
            )
        ]

    def __str__(self):
        return f"{self.form} - {self.label}"


class Submission(AbstractBaseModel):
    """Represents a submission of a Form.

    Attributes:
    - form (models.ForeignKey): The Form associated with this submission.

    Related Names:
    - submissions: A reverse relation to access submissions related to a Form.
    - product: The associated product for this submission.
    """

    form = models.ForeignKey(
        Form,
        related_name="submissions",
        on_delete=models.CASCADE,
        verbose_name=_("Form"),
    )
    product = models.ForeignKey(
        Product,
        related_name="submissions",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Product"),
    )

    def __str__(self):
        return f"{self.form}"


class SubmissionValues(AbstractBaseModel):
    """Represents the values of fields submitted within a Form.

    Attributes:
    - submission (models.ForeignKey): The Submission associated with these
        values.
    - field (models.ForeignKey): The FormField associated with these values.
    - value (models.CharField): The actual value for the field.

    Meta:
    - constraints: Defines a UniqueConstraint to ensure the uniqueness
        of pairs (submission, field).
    """

    submission = models.ForeignKey(
        Submission,
        related_name="values",
        on_delete=models.CASCADE,
        verbose_name=_("Submission"),
    )
    field = models.ForeignKey(
        FormField,
        related_name="values",
        on_delete=models.CASCADE,
        verbose_name=_("Field"),
    )
    value = models.CharField(max_length=100, verbose_name=_("Value"))

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["submission", "field"], name="unique_submission_field"
            )
        ]

    def clean(self):
        """Validates that the field and submission belong to the same Form.

        Raises:
        ValidationError: If the field and submission do not belong to the same
            Form.
        """
        if self.field.form != self.submission.form:
            raise ValidationError(
                _("Field and Submission must belong to the same Form.")
            )

    def __str__(self):
        return f"{self.submission} - {self.field} - {self.value}"
