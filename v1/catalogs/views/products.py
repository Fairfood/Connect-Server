from base.request_handler.views import IdDecodeModelViewSet
from v1.catalogs.filters import PremiumFilterSet
from v1.catalogs.filters import ProductFilterSet
from v1.catalogs.models.product_models import Premium
from v1.catalogs.models.product_models import Product
from v1.catalogs.serializers.products import PremiumSerializer
from v1.catalogs.serializers.products import ProductSerializer


class ProductViewSet(IdDecodeModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    http_method_names = ("get",)
    filterset_class = ProductFilterSet


class PremiumViewSet(IdDecodeModelViewSet):
    queryset = Premium.objects.all()
    serializer_class = PremiumSerializer
    http_method_names = ("get",)
    filterset_class = PremiumFilterSet
