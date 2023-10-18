"""Views related to category."""
from rest_framework import filters

from base.request_handler.views import IdDecodeModelViewSet
from v1.catalogs.models import common_models as catalog_models
from v1.catalogs.serializers import category as category_serializers


class CategoryViewSet(IdDecodeModelViewSet):
    """View to list, create , update and delete category data.

    View to list, create , update and delete category data. View to
    list, create , update and delete category data.
    """

    http_method_names = ["get", "post", "patch", "delete"]
    filter_backends = [
        filters.SearchFilter,
    ]
    search_fields = [
        "name",
    ]
    filterset_fields = [
        "type",
    ]
    serializer_class = category_serializers.CategorySerializer
    queryset = catalog_models.Category.objects.all()
