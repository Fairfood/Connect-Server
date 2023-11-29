from django.db import transaction
from rest_framework.serializers import CharField
from rest_framework.serializers import SerializerMethodField

from base.authentication import utilities as utils
from base.drf import serializers
from v1.catalogs.models import product_models
from v1.supply_chains.models.company_models import CompanyProduct


class ProductSerializer(serializers.DynamicModelSerializer):
    """
    Serializer for the Product model.
    """

    premiums = SerializerMethodField()

    class Meta:
        model = product_models.Product
        fields = "__all__"

    def get_premiums(self, instance):
        """
        Get the premiums associated with the company product.

        Returns:
            list: A list of premiums associated with the product.
        """
        entity = utils.get_current_entity()
        if not entity:
            return []
        try:
            c_product = CompanyProduct.objects.get(
                company=entity, product=instance
            )
        except CompanyProduct.DoesNotExist:
            return []

        return c_product.premiums.values_list("id", flat=True)


class ConnectCardSerializer(serializers.DynamicModelSerializer):
    """
    Serializer for the ConnectCard model.
    """

    card_id = CharField(validators=[])

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

    options = PremiumOptionSeriazer(
        many=True, required=False, exclude_fields=("premium",)
    )

    class Meta:
        model = product_models.Premium
        fields = "__all__"

    @transaction.atomic
    def create(self, validated_data):
        options = validated_data.pop("options", [])
        instance = super().create(validated_data)
        for option in options:
            option["premium"] = instance
        self.fields["options"].create(options)
        return instance
