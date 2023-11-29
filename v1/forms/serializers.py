from django.db import transaction

from base.drf.serializers import DynamicModelSerializer
from v1.catalogs.serializers.products import ProductSerializer
from v1.forms.models import Form
from v1.forms.models import FormField
from v1.forms.models import Submission
from v1.forms.models import SubmissionValues


class FormFieldSerializer(DynamicModelSerializer):
    """Serializer for the FormField model."""

    class Meta:
        model = FormField
        fields = "__all__"


class FormSerializer(DynamicModelSerializer):
    """
    Serializer for the Form model.

    Attributes:
    - product (ProductSerializer): A nested serializer for the associated
        Product model.
    - fields (FormFieldSerializer): A nested serializer for the associated
        FormField models.

    """

    product = ProductSerializer(read_only=True, fields=("id", "name"))
    fields = FormFieldSerializer(
        many=True, read_only=True, exclude_fields=("form",)
    )

    class Meta:
        model = Form
        fields = "__all__"


class SubmissionValuesSerializer(DynamicModelSerializer):
    """
    Serializer for the SubmissionValues model.

    Attributes:
    - field_details (FormFieldSerializer): A nested serializer for the
        associated FormField model.

    """

    field_details = FormFieldSerializer(
        source="field", read_only=True, exclude_fields=("form",)
    )

    class Meta:
        model = SubmissionValues
        fields = "__all__"


class SubmissionSerializer(DynamicModelSerializer):
    """
    Serializer for the Submission model.

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
        """
        Custom creation method for creating Submission and associated
        SubmissionValues.

        Args:
        - validated_data (dict): Validated data for creating the Submission
            instance.

        Returns:
        Submission: The created Submission instance.
        """
        values = validated_data.pop("values")
        instance = super().create(validated_data)
        for val in values:
            SubmissionValues.objects.create(submission=instance, **val)
        return instance
