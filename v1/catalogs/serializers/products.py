from django.db import transaction
from rest_framework.serializers import CharField
from rest_framework.serializers import SerializerMethodField
from rest_framework.serializers import ValidationError

from base.authentication import utilities as utils
from base.drf import serializers
from v1.catalogs.models import product_models
from v1.supply_chains.models.company_models import CompanyProduct


class ProductSerializer(serializers.DynamicModelSerializer):
    """Serializer for the Product model."""

    premiums = SerializerMethodField()
    is_active = SerializerMethodField()

    class Meta:
        model = product_models.Product
        fields = "__all__"

    def _get_company_product(self, instance):
        """Get the company product associated with the product."""
        entity = utils.get_current_entity()
        if not entity:
            return None
        try:
            return CompanyProduct.objects.get(company=entity, product=instance)
        except CompanyProduct.DoesNotExist:
            return None

    def get_premiums(self, instance):
        """Get the premiums associated with the company product.

        Returns:
            list: A list of premiums associated with the product.
        """
        c_product = self._get_company_product(instance)
        return (
            c_product.premiums.values_list("id", flat=True)
            if c_product
            else []
        )

    def get_is_active(self, instance):
        """Get the is_active associated with the company product.

        Returns:
            list: A list of is_active associated with the product.
        """
        c_product = self._get_company_product(instance)
        return c_product.is_active if c_product else False


class ConnectCardSerializer(serializers.DynamicModelSerializer):
    """Serializer for the ConnectCard model."""

    def __init__(self, *args, entity_card=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity_card = entity_card

    card_id = CharField(validators=[], required=False)

    class Meta:
        model = product_models.ConnectCard
        fields = "__all__"

    def create(self, validated_data):
        """Create a new product instance.

        Args:
            validated_data (dict): The validated data for creating the product.

        Returns:
            instance: The created product instance.

        Raises:
            ValidationError: If the `card_id` is not provided.
        """
        display_id = validated_data.get("display_id")
        card_id = validated_data.get("card_id")

        if not display_id and not card_id:
            raise ValidationError(
                "Either 'display_id' or 'card_id' must be provided."
            )

        d_instance = c_instance = cd_instance = None

        if display_id and not card_id:
            # check if the display_id is already exists
            d_instance = product_models.ConnectCard.objects.filter(
                display_id=display_id).first()
            # if entity card exist and card not exist
            if not d_instance and self.entity_card:
                # if the entity card exists check if the display_id 
                # is already exists.
                if (self.entity_card.card.card_id and 
                    not self.entity_card.card.display_id):
                    self.entity_card.card.display_id = display_id
                    self.entity_card.card.save()
                    return self.entity_card.card
                else:
                    self.entity_card.is_active = False
                    self.entity_card.save()

            # if entity card  and connect card exist
            if d_instance and self.entity_card:
                if self.entity_card.card != d_instance:
                    self.entity_card.is_active = False
                    self.entity_card.save()


        if card_id and not display_id:
            # check if the card_id is already exists
            c_instance = product_models.ConnectCard.objects.filter(
                card_id=card_id).first()
            # if entity card exist and card not exist
            if not c_instance and self.entity_card:
                # if the entity card exists check if the display_id 
                # is already exists.
                if (self.entity_card.card.display_id and 
                    not self.entity_card.card.card_id):
                    self.entity_card.card.card_id = card_id
                    self.entity_card.card.save()
                    return self.entity_card.card
                else:
                    self.entity_card.is_active = False
                    self.entity_card.save()

            # if entity card and connect card exist
            if c_instance and self.entity_card:
                if self.entity_card.card != c_instance:
                    self.entity_card.is_active = False
                    self.entity_card.save()


        if card_id and display_id:
            # check if the card_id is already exists
            cd_instance = product_models.ConnectCard.objects.filter(
                card_id=card_id, display_id=display_id).first()
            if cd_instance and self.entity_card:
                if cd_instance != self.entity_card.card:
                    self.entity_card.is_active = False
                    self.entity_card.save()


        instance = d_instance or c_instance or cd_instance

        if not instance:
            return super().create(validated_data)
        return instance


class PremiumOptionSeriazer(serializers.DynamicModelSerializer):
    """Serializer for the PremiumOption model."""

    class Meta:
        model = product_models.PremiumOption
        fields = "__all__"


class PremiumRangeSerializer(serializers.DynamicModelSerializer):
    """Serializer for the PremiumRange model."""

    class Meta:
        model = product_models.PremiumRange
        fields = "__all__"


class PremiumSerializer(serializers.DynamicModelSerializer):
    """Serializer for the Premium model.

    This serializer includes details about premium options and allows
    creating instances of the Premium model along with associated
    premium options.
    """

    options = PremiumOptionSeriazer(
        many=True, required=False, exclude_fields=("premium",)
    )
    ranges = PremiumRangeSerializer(
        many=True, required=False, exclude_fields=("premium",)
    )

    class Meta:
        model = product_models.Premium
        fields = "__all__"

    @transaction.atomic
    def create(self, validated_data):
        """Create method for PremiumSerializer.

        Handles the creation of Premium instances, including the creation of
        associated premium options.

        Args:
            validated_data (dict): The validated data for creating the Premium
            instance.

        Returns:
            Premium: The created Premium instance.
        """
        options = validated_data.pop("options", [])
        ranges = validated_data.pop("ranges", [])
        instance = super().create(validated_data)
        for option in options:
            option["premium"] = instance
        for range in ranges:
            range["premium"] = instance
        self.fields["options"].create(options)
        self.fields["ranges"].create(ranges)
        return instance
