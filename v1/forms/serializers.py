from base.drf.serializers import DynamicModelSerializer
from v1.forms.models import Form
from v1.forms.models import FormValues
from v1.forms.models import ReferenceForm
from v1.forms.models import ReferenceFormField


class ReferenceFormFieldSerializer(DynamicModelSerializer):
    """
    Serializer for the ReferenceFormField model.
    """

    class Meta:
        model = ReferenceFormField
        fields = "__all__"


class ReferenceFormSerializer(DynamicModelSerializer):
    """
    Serializer for the RefferenceForm model.
    """

    fields = ReferenceFormFieldSerializer(many=True, read_only=True)

    class Meta:
        model = ReferenceForm
        fields = "__all__"


class FormValuesSerializer(DynamicModelSerializer):
    """
    Serializer for the FormField model.
    """

    class Meta:
        model = FormValues
        fields = "__all__"


class FormSerializer(DynamicModelSerializer):
    """
    Serializer for the Form model.
    """

    values = FormValuesSerializer(many=True)

    class Meta:
        model = Form
        fields = "__all__"
