from django.db import transaction
from rest_framework import serializers

from base.authentication import utilities as utils
from base.drf.fields import SerializableRelatedField
from base.drf.serializers import DynamicModelSerializer
from v1.accounts.serializers.user import UserSerializer
from v1.catalogs.models.common_models import Currency
from v1.catalogs.serializers.currency import CurrencySerializer
from v1.catalogs.serializers.products import ConnectCardSerializer
from v1.catalogs.serializers.products import ProductSerializer
from v1.forms.serializers import FormSerializer
from v1.forms.serializers import SubmissionSerializer
from v1.supply_chains.models.base_models import Entity
from v1.supply_chains.models.base_models import EntityCard
from v1.supply_chains.models.company_models import Company
from v1.supply_chains.models.company_models import CompanyFieldVisibilty
from v1.supply_chains.models.company_models import CompanyMember
from v1.supply_chains.models.company_models import CompanyProduct
from v1.supply_chains.models.farmer_models import Farmer


class EntityCardSerializer(DynamicModelSerializer):
    """
    Serializer for the EntityCard model.
    """

    card = ConnectCardSerializer()

    class Meta:
        model = EntityCard
        fields = "__all__"
        read_only_fields = ("is_active",)

    def create(self, validated_data):
        """Override the default create."""
        card_data = validated_data.pop("card")
        card = self.fields["card"].create(card_data)
        validated_data["card"] = card
        try:
            instance = EntityCard.objects.get(**validated_data)
            instance.is_active = True
            instance.save()
            return instance
        except EntityCard.DoesNotExist:
            return super().create(validated_data)


class EntitySerializer(DynamicModelSerializer):
    """
    Serializer for the Entity model.
    """

    name = serializers.CharField(read_only=True)
    entity_card = EntityCardSerializer(read_only=True)

    class Meta:
        model = Entity
        fields = "__all__"


class CompanyFieldVisibiltySerilizer(DynamicModelSerializer):
    class Meta:
        model = CompanyFieldVisibilty
        fields = "__all__"


class CompanySerializer(DynamicModelSerializer):
    """
    Serializer for the Company model.
    """

    currency = CurrencySerializer(read_only=True)
    buyer = EntitySerializer(
        read_only=True,
        fields=("id", "name", "image", "description", "entity_card"),
    )
    entity_card = EntityCardSerializer(read_only=True)
    forms = FormSerializer(
        many=True, read_only=True, exclude_fields=("owner",)
    )
    field_visibilties = CompanyFieldVisibiltySerilizer(
        many=True, read_only=True
    )
    owned_premiums = SerializableRelatedField(read_only=True, many=True)

    class Meta:
        model = Company
        fields = "__all__"


# TODO: Remove this serializer after the migration is complete.
class CompanyCreateSerializer(DynamicModelSerializer):
    """
    Serializer for the Company model.
    """

    currency = serializers.CharField(required=False)

    class Meta:
        model = Company
        fields = "__all__"

    def create(self, validated_data):
        """Override the default create."""
        currency = validated_data.pop("currency", None)
        if currency:
            try:
                currency_obj = Currency.objects.get(pk=currency)
            except Currency.DoesNotExist:
                currency_obj = Currency.objects.get(code=currency)
            validated_data["currency"] = currency_obj
        return super().create(validated_data)


class CompanyMemerSerializer(DynamicModelSerializer):
    user = UserSerializer(
        fields=(
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "dob",
            "address",
            "language",
        )
    )

    class Meta:
        model = CompanyMember
        fields = "__all__"

    def create(self, validated_data):
        user = self.fields["user"].create(validated_data.pop("user"))
        validated_data["user"] = user
        return super().create(validated_data)


class CompanyProductSerializer(DynamicModelSerializer):

    product = ProductSerializer(exclude_fields=("premiums",))

    class Meta:
        model = CompanyProduct
        fields = "__all__"

    def create(self, validated_data):
        product = validated_data.pop("product")
        product = self.fields["product"].create(product)
        validated_data["product"] = product
        return super().create(validated_data)


class FarmerSerializer(DynamicModelSerializer):
    """
    Serializer for the Farmer model.
    """

    entity_card = EntityCardSerializer(read_only=True)
    submission = SubmissionSerializer(required=False)

    class Meta:
        model = Farmer
        fields = "__all__"

    @transaction.atomic
    def create(self, validated_data):
        """Override the default create."""
        user = utils.get_current_user()
        if not user.is_admin:
            validated_data["buyer"] = utils.get_current_entity()
        submission_data = validated_data.pop("submission", None)
        instance = super().create(validated_data)
        if submission_data:
            submission = self.fields["submission"].create(submission_data)
            instance.submission = submission
        instance.save()
        return instance
