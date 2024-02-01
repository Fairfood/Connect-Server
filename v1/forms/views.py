# from django.shortcuts import render
# Create your views here.
from .models import Form
from base.request_handler.views import IdDecodeModelViewSet
from v1.forms.serializers import FormSerializer


class FormViewSet(IdDecodeModelViewSet):
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
    http_method_names = ["get", "post"]
