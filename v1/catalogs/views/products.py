from base.request_handler.views import IdDecodeModelViewSet
from v1.catalogs.filters import PremiumFilterSet
from v1.catalogs.filters import ProductFilterSet
from v1.catalogs.models.product_models import ConnectCard
from v1.catalogs.models.product_models import Premium
from v1.catalogs.models.product_models import Product
from v1.catalogs.serializers.products import ConnectCardSerializer
from v1.catalogs.serializers.products import PremiumSerializer
from v1.catalogs.serializers.products import ProductSerializer


class ProductViewSet(IdDecodeModelViewSet):
    """A viewset for viewing Product instances.

    This viewset extends the IdDecodeModelViewSet and provides
    customization for viewing Product instances in the API.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    http_method_names = ("get",)
    filterset_class = ProductFilterSet


class PremiumViewSet(IdDecodeModelViewSet):
    """A viewset for viewing and creating Premium instances.

    This viewset extends the IdDecodeModelViewSet and provides
    customization for viewing and creating Premium instances in the API.
    """

    queryset = Premium.objects.all()
    serializer_class = PremiumSerializer
    http_method_names = ("get", "post")
    filterset_class = PremiumFilterSet


class ConnectCardViewSet(IdDecodeModelViewSet):
    """A viewset for viewing and creating ConnectCard instances.

    This viewset extends the IdDecodeModelViewSet and provides
    customization for viewing and creating ConnectCard instances in the
    API.
    """

    queryset = ConnectCard.objects.all()
    serializer_class = ConnectCardSerializer
    http_method_names = ("get", "post")
    # filterset_class = ConnectCardFilterSet
