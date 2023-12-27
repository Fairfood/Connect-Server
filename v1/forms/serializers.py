from django.db import transaction
from rest_framework import serializers

from . import constants as from_consts
from base.drf.serializers import DynamicModelSerializer
from v1.catalogs.serializers.products import ProductSerializer
from v1.forms.models import Form
from v1.forms.models import FormField
from v1.forms.models import FormFieldConfig
from v1.forms.models import Submission
from v1.forms.models import SubmissionValues
from v1.supply_chains.models.company_models import CompanyProduct


class FormFieldSerializer(DynamicModelSerializer):
    """Serializer for the FormField model."""

    class Meta:
        model = FormField
        fields = "__all__"


class FormFieldConfigSerializer(DynamicModelSerializer):
    """Serializer for the FormFieldConfig model."""

    class Meta:
        model = FormFieldConfig
        fields = "__all__"

    def create(self, validated_data):
        """Custom creation method for creating FormFieldConfig."""
        form = validated_data.get("form")
        key = validated_data.get("key")
        try:
            instance = self.Meta.model.objects.get(form=form, key=key)
            return super().update(instance, validated_data)
        except self.Meta.model.DoesNotExist:
            return super().create(validated_data)


class FormSerializer(DynamicModelSerializer):
    """Serializer for the Form model.

    Attributes:
    - product (ProductSerializer): A nested serializer for the associated
        Product model.
    - fields (FormFieldSerializer): A nested serializer for the associated
        FormField models.
    """

    products = ProductSerializer(
        many=True, read_only=True, fields=("id", "name")
    )
    fields = FormFieldSerializer(
        many=True, exclude_fields=("form",), required=True
    )
    field_config = FormFieldConfigSerializer(
        many=True, exclude_fields=("form",), required=False
    )

    class Meta:
        model = Form
        fields = "__all__"

    def create(self, validated_data):
        """Custom creation method for creating Form and associated FormFields.

        Args:
        - validated_data (dict): Validated data for creating the Form instance.

        Returns:
        Form: The created Form instance.
        """
        fields = validated_data.pop("fields")
        field_config = validated_data.pop("field_config", [])
        instance = super().create(validated_data)
        for field in fields:
            field["form"] = instance
        self.fields["fields"].create(fields)
        for config in field_config:
            config["form"] = instance
        self.fields["field_config"].create(field_config)
        if instance.form_type == from_consts.FormType.PRODUCT:
            company_products = CompanyProduct.objects.filter(
                company=instance.owner
            )
            [product.forms.add(instance) for product in company_products]
        return instance


class SubmissionValuesSerializer(DynamicModelSerializer):
    """Serializer for the SubmissionValues model.

    Attributes:
    - field_details (FormFieldSerializer): A nested serializer for the
        associated FormField model.
    """

    field_details = FormFieldSerializer(
        source="field", read_only=True, exclude_fields=("form",)
    )
    field = serializers.CharField(write_only=True)

    class Meta:
        model = SubmissionValues
        fields = "__all__"

    def create(self, validated_data):
        """Create method for the serializer.

        This method handles the creation of an instance, specifically for
        associating a field with the instance.

        Args:
            validated_data (dict): The validated data for creating the
            instance.

        Returns:
            object: The created instance.
        """
        field = validated_data.pop("field")
        try:
            field = FormField.objects.get(pk=field)
        except FormField.DoesNotExist:
            field = FormField.objects.get(key=field)
        validated_data["field"] = field
        return super().create(validated_data)


class SubmissionSerializer(DynamicModelSerializer):
    """Serializer for the Submission model.

    Attributes:
    - form_details (FormSerializer): A nested serializer for the associated
        Form model.
    - value_details (SubmissionValuesSerializer): A nested serializer for the
        associated SubmissionValues models.
    - values (SubmissionValuesSerializer): A nested serializer for the
        write-only SubmissionValues models.
    """

    form_details = FormSerializer(
        source="form", read_only=True, fields=("id", "product", "form_type")
    )
    values = SubmissionValuesSerializer(
        many=True, exclude_fields=("submission",)
    )

    class Meta:
        model = Submission
        fields = "__all__"

    @transaction.atomic
    def create(self, validated_data):
        """Custom creation method for creating Submission and associated
        SubmissionValues.

        Args:
        - validated_data (dict): Validated data for creating the Submission
            instance.

        Returns:
        Submission: The created Submission instance.
        """
        values = validated_data.pop("values")
        instance = super().create(validated_data)
        for value in values:
            value["submission"] = instance
        self.fields["values"].create(values)
        return instance
