from base.drf import serializers
from v1.catalogs.models import product_models


class ProductSerializer(serializers.DynamicModelSerializers):
    """
    Serializer for the Product model.
    """

    class Meta:
        model = product_models.Product
        fields = "__all__"


class ConnectCardSerializer(serializers.DynamicModelSerializers):
    """
    Serializer for the ConnectCard model.
    """

    class Meta:
        model = product_models.ConnectCard
        fields = "__all__"


class PremiumSerializer(serializers.DynamicModelSerializers):
    """
    Serializer for the Premium model.
    """

    class Meta:
        model = product_models.Premium
        fields = "__all__"
