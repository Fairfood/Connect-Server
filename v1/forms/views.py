# from django.shortcuts import render
# Create your views here.
from .models import Form
from base.request_handler.views import IDDEcodeScopeViewset
from v1.forms.serializers import FormSerializer


class FormViewSet(IDDEcodeScopeViewset):
    """ViewSet for the Form model.

    Attributes:
    - queryset (QuerySet): The queryset of the model.
    - serializer_class (Serializer): The serializer class of the model.
    - filterset_fields (list): The list of fields to filter the queryset.
    - search_fields (list): The list of fields to search in the queryset.
    - ordering_fields (list): The list of fields to order the queryset.
    """

    queryset = Form.objects.all()
    serializer_class = FormSerializer
    resource_types = ["catalog"]
    http_method_names = ["get", "post"]
