from base.drf import serializers
from v1.catalogs.models import product_models


class ProductSerializer(serializers.DynamicModelSerializer):
    """
    Serializer for the Product model.
    """

    class Meta:
        model = product_models.Product
        fields = "__all__"


class ConnectCardSerializer(serializers.DynamicModelSerializer):
    """
    Serializer for the ConnectCard model.
    """

    class Meta:
        model = product_models.ConnectCard
        fields = "__all__"

    def create(self, validated_data):
        """
        Create a new ConnectCard object or update an existing one.

        This method is overridden to either create a new ConnectCard object or,
        if a card with the provided `card_id` already exists, update the
        existing card with the provided data.

        Args:
            validated_data (dict): A dictionary of validated data to create or
                update a ConnectCard.

        Returns:
            ConnectCard: The created or updated ConnectCard object.
        """
        card_id = validated_data.get("card_id")
        try:
            instance = product_models.ConnectCard.objects.get(card_id=card_id)
            return super().update(instance, validated_data)
        except product_models.ConnectCard.DoesNotExist:
            return super().create(validated_data)


class PremiumOptionSeriazer(serializers.DynamicModelSerializer):
    """
    Serializer for the PremiumOption model.
    """

    class Meta:
        model = product_models.PremiumOption
        fields = "__all__"


class PremiumSerializer(serializers.DynamicModelSerializer):
    """
    Serializer for the Premium model.
    """

    options = PremiumOptionSeriazer(many=True, read_only=True)

    class Meta:
        model = product_models.Premium
        fields = "__all__"
