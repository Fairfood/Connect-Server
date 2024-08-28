from typing import Any, Dict

from django.db import transaction
from rest_framework.serializers import (CharField, SerializerMethodField,
                                        ValidationError)

from base.authentication import utilities as utils
from base.drf import serializers
from v1.catalogs.models import product_models
from v1.supply_chains.models.base_models import EntityCard
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
        return c_product.premiums.values_list("id", flat=True) if c_product else []

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

    def deactivate_entity_cards(
        self,
        associated_card: "product_models.ConnectCard",
    ) -> None:
        """
        Deactivates all active EntityCard objects associated with the given ConnectCard.

        Args:
            associated_card (ConnectCard): The ConnectCard for which associated EntityCard objects should be deactivated.

        Returns:
            None
        """
        # Retrieve all active EntityCard objects associated with the provided ConnectCard
        active_entity_cards = EntityCard.objects.filter(
            card=associated_card, is_active=True
        ).all()

        # Deactivate each EntityCard by setting is_active to False and saving the change
        for entity_card in active_entity_cards:
            entity_card.is_active = False
            entity_card.save()

    def create(self, validated_data: Dict[str, Any]) -> "product_models.ConnectCard":
        """
        Retrieves or creates a ConnectCard based on provided card_data. If both display_id and card_id are provided,
        it checks for existing cards and handles potential conflicts.

        Args:
            validated_data (Dict[str, Any]): A dictionary containing 'display_id' and/or 'card_id' to identify the ConnectCard.

        Returns:
            ConnectCard: The retrieved or newly created ConnectCard object.

        Raises:
            serializers.ValidationError: If neither 'display_id' nor 'card_id' is provided in card_data.
        """
        display_id = validated_data.get("display_id")
        card_id = validated_data.get("card_id")

        # Validate that at least one identifier (display_id or card_id) is provided
        if not display_id and not card_id:
            raise ValidationError("Either 'display_id' or 'card_id' must be provided.")

        # If both display_id and card_id are provided
        if display_id and card_id:
            # Retrieve any active ConnectCards by display_id or card_id
            qr_card = product_models.ConnectCard.objects.filter(
                display_id=display_id, is_active=True
            ).first()
            nfc_card = product_models.ConnectCard.objects.filter(
                card_id=card_id, is_active=True
            ).first()

            # If both cards exist and are the same instance, deactivate entity cards and return the card
            if qr_card and nfc_card:
                if qr_card.pk == nfc_card.pk:  # Both refer to the same card
                    self.deactivate_entity_cards(qr_card)
                    return qr_card
                else:
                    # Deactivate entity cards and the cards themselves, then create a new combined card
                    self.deactivate_entity_cards(qr_card)
                    self.deactivate_entity_cards(nfc_card)

                    # inactivate both connect card
                    qr_card.is_active = False
                    qr_card.save()
                    nfc_card.is_active = False
                    nfc_card.save()

            # If only one of the cards exists, update it with the other card's ID and return it
            elif qr_card and not nfc_card:
                self.deactivate_entity_cards(qr_card)
                qr_card.card_id = card_id
                qr_card.save()
                return qr_card
            elif not qr_card and nfc_card:
                self.deactivate_entity_cards(nfc_card)
                nfc_card.display_id = display_id
                nfc_card.save()
                return nfc_card

        # If only one of display_id or card_id is provided
        else:
            card_data = {"is_active": True}
            check_field = ""
            if display_id and not card_id:
                card_data["display_id"] = display_id
                check_field = "display_id"
            else:
                card_data["card_id"] = card_id
                check_field = "card_id"

            # Retrieve the card based on the provided identifier
            card = product_models.ConnectCard.objects.filter(**card_data).first()
            if card:
                self.deactivate_entity_cards(card)
                return card
            else:
                # If an entity_card is provided and it doesn't have the identifier, update and return it
                if (
                    self.entity_card
                    and hasattr(self.entity_card.card, check_field)
                    and not getattr(self.entity_card.card, check_field, None)
                ):
                    setattr(self.entity_card.card, check_field, card_data[check_field])
                    self.entity_card.card.save()
                    return self.entity_card.card

        return super().create(validated_data)


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
