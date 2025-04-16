

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from base.authentication import utilities as utils
from base.drf.fields import (PhoneNumberField, RoundingDecimalField,
                             SerializableRelatedField, UnixDateTimeField)
from base.drf.serializers import DynamicModelSerializer
from utilities.country_data import COUNTRY_LIST, COUNTRY_WITH_PROVINCE
from v1.accounts.serializers import user as user_serializers
from v1.catalogs.models.common_models import Currency
from v1.catalogs.models.product_models import Premium, Product
from v1.catalogs.serializers.currency import CurrencySerializer
from v1.catalogs.serializers.products import (ConnectCardSerializer,
                                              PremiumSerializer,
                                              ProductSerializer)
from v1.forms.serializers import FormSerializer, SubmissionSerializer
from v1.supply_chains.models.base_models import Entity, EntityBuyer, EntityCard
from v1.supply_chains.models.company_models import (Company,
                                                    CompanyFieldVisibilty,
                                                    CompanyMember,
                                                    CompanyProduct)
from v1.supply_chains.models.farmer_models import Farmer, FarmerService
from v1.supply_chains.validators import (validate_coordinates,
                                         validate_geojson_polygon)
from v1.transactions.models.payment_models import PaymentTransaction
from v1.transactions.models.transaction_models import ProductTransaction


class EntityCardSerializer(DynamicModelSerializer):
    """Serializer for the EntityCard model."""

    card = ConnectCardSerializer()

    class Meta:
        model = EntityCard
        fields = "__all__"
        read_only_fields = ("is_active",)

    def create(self, validated_data):
        """Override the default create."""
        card_data = validated_data.pop("card")
        entity_id = validated_data.get("entity")

        entity_card = EntityCard.objects.filter(
            entity=entity_id, is_active=True
        ).first()

        card_serializer = ConnectCardSerializer(data=card_data, entity_card=entity_card)

        card_serializer.is_valid(raise_exception=True)
        card = card_serializer.save()
        # Always return a card
        if entity_card:
            if card.pk == entity_card.card.pk:
                # Possibly all the cards became inactive
                entity_card.is_active = True
                entity_card.save()
                return entity_card
            if card.pk != entity_card.card.pk:
                entity_card.is_active = False
                entity_card.save()

        validated_data["card"] = card
        return super().create(validated_data)


class EntitySerializer(DynamicModelSerializer):
    """Serializer for the Entity model."""

    name = serializers.CharField(read_only=True)
    entity_card = serializers.SerializerMethodField()

    class Meta:
        model = Entity
        fields = "__all__"

    def get_entity_card(self, obj):
        """Fetch all EntityCard instances related to the company."""
        entity_cards = EntityCard.objects.filter(entity=obj, is_active=True)
        return EntityCardSerializer(entity_cards, many=True, read_only=True).data


class EntityBuyerReadOnlySerializer(DynamicModelSerializer):
    """Serializer for the Entity buyer model."""

    id = serializers.CharField(read_only=True, source="buyer.id")
    name = serializers.CharField(read_only=True, source="buyer.name")
    image = serializers.ImageField(read_only=True, source="buyer.image")
    description = serializers.CharField(read_only=True, source="buyer.description")
    entity_card = serializers.SerializerMethodField()

    class Meta:
        model = EntityBuyer
        fields = ("id", "name", "image", "description", "entity_card", "is_default",)

    def get_entity_card(self, obj):
        """Fetch all EntityCard instances related to the company."""
        if obj.buyer.entity_card:
            return EntityCardSerializer(obj.buyer.entity_card, read_only=True).data
        return None


class EntityBuyerReadOnlySingleEntityCardSerializer(EntityBuyerReadOnlySerializer):
    """Serializer for the Entity buyer model."""

    entity_card = serializers.SerializerMethodField()

    def get_entity_card(self, obj):
        """Fetch all EntityCard instances related to the company."""
        if obj.buyer.entity_card:
            return [EntityCardSerializer(obj.buyer.entity_card, read_only=True).data]
        return []


class EntityBuyerSerializer(DynamicModelSerializer):
    id = serializers.CharField(read_only=True)
    is_default = serializers.BooleanField(read_only=True)
    company = serializers.PrimaryKeyRelatedField(
        required=False,
        queryset=Entity.objects.all(), source = "entity"
    )
    buyer = serializers.PrimaryKeyRelatedField(
        required=False,
        queryset=Entity.objects.all(),
    )

    class Meta:
        model = EntityBuyer
        fields = ("id", "company", "buyer", "is_default",)

    def validate(self, attrs):
        if EntityBuyer.objects.filter(entity=attrs["entity"], buyer=attrs["buyer"]).exists():
            raise serializers.ValidationError({"buyer": _("buyer company relation already exist.")})
        return super().validate(attrs)


class CompanyFieldVisibiltySerilizer(DynamicModelSerializer):
    """Serializer for CompanyFieldVisibilty.

    This serializer includes all fields for the CompanyFieldVisibilty
    model.
    """

    class Meta:
        model = CompanyFieldVisibilty
        fields = "__all__"


class CompanySerializer(DynamicModelSerializer):
    """Serializer for the Company model."""

    currency = CurrencySerializer(read_only=True)
    buyers = serializers.SerializerMethodField(method_name="get_buyers")
    buyer = serializers.SerializerMethodField(method_name="get_buyer")
    entity_card = EntityCardSerializer(read_only=True)
    forms = FormSerializer(many=True, read_only=True, exclude_fields=("owner",))
    field_visibilties = CompanyFieldVisibiltySerilizer(many=True, read_only=True)
    owned_premiums = SerializableRelatedField(read_only=True, many=True)

    class Meta:
        model = Company
        fields = "__all__"

    def get_buyers(self, obj):
        buyers = EntityBuyer.objects.filter(entity=obj).all()
        if buyers:
            serializer = EntityBuyerReadOnlySerializer(
                instance=buyers,
                many=True
            )
            return serializer.data
        return []

    def get_buyer(self, obj):
        default_buyer = EntityBuyer.objects.filter(entity=obj, is_default=True).first()
        if default_buyer:
            serializer = EntityBuyerReadOnlySingleEntityCardSerializer(
                instance=default_buyer
            )
            return serializer.data
        return None


# TODO: Remove this serializer after the migration is complete.
class CompanyCreateSerializer(DynamicModelSerializer):
    """Serializer for the Company model."""

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
        image = None
        if "image" in validated_data:
            image  = validated_data.pop("image")
        company_obj =  super().create(validated_data)
        if image:
            company_obj.image = image
            company_obj.save()
        return company_obj


class CompanyMemerMiniSerializer(DynamicModelSerializer):
    """Serializer for CompanyMember.

    This serializer includes details about the user associated with the
    company member, using a nested UserSerializer.
    """

    # user = UserSerializer(
    #     fields=(
    #         "id",
    #         "email",
    #         "first_name",
    #         "last_name",
    #         "phone",
    #         "dob",
    #         "address",
    #         "language",
    #     )
    # )

    class Meta:
        model = CompanyMember
        fields = "__all__"

    # def create(self, validated_data):
    #     """Create method for CompanyMemerSerializer.

    #     Handles the creation of CompanyMember instances, including the
    #     creation of the associated user.
    #     """
    #     user = self.fields["user"].create(validated_data.pop("user"))
    #     validated_data["user"] = user
    #     return super().create(validated_data)


class CompanyProductSerializer(DynamicModelSerializer):
    """Serializer for CompanyProduct.

    This serializer includes product details and allows specifying
    either the product instance or its ID during validation and
    creation.
    """

    product = ProductSerializer(exclude_fields=("premiums",), required=False)
    product_id = serializers.CharField(required=False)

    class Meta:
        model = CompanyProduct
        fields = "__all__"

    def validate(self, data):
        """Validate method for CompanyProductSerializer.

        Validates that either the product or product_id is provided.
        """
        product = data.get("product", None)
        product_id = data.get("product_id", None)
        if not product and not product_id:
            raise serializers.ValidationError(
                "Either product or product_id is required."
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        """Create method for CompanyProductSerializer.

        Handles the creation of CompanyProduct instances, either by
        using an existing product with an ID or creating a new product.
        """
        product = validated_data.pop("product", None)
        product_id = validated_data.pop("product_id", None)
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError(
                    f"Product with id {product_id} does not exist."
                )
        else:
            product = self.fields["product"].create(product)
        validated_data["product"] = product

        try:
            data = {
                "product": validated_data["product"],
                "company": validated_data["company"],
            }
            instance = CompanyProduct.objects.get(**data)
            return instance
        except CompanyProduct.DoesNotExist:
            return super().create(validated_data)


class ExternalServiceSerializer(DynamicModelSerializer):
    id = serializers.CharField(read_only=True, source="service.id")
    link = serializers.SerializerMethodField(method_name="get_service_link")
    name = serializers.CharField(read_only=True, source="service.name")
    description = serializers.CharField(read_only=True, source="service.description")
    icon = serializers.ImageField(read_only=True, source="service.icon")

    class Meta:
        model = FarmerService
        fields = ["id", "name", "description", "icon", "link",]

    def get_service_link(self, obj):
        refernce_id = obj.refernce_id
        return obj.service.service_url.replace("{{refernce_id}}", refernce_id)


class ExternalServiceSerializer(DynamicModelSerializer):
    id = serializers.CharField(read_only=True, source="service.id")
    link = serializers.SerializerMethodField(method_name="get_service_link")
    name = serializers.CharField(read_only=True, source="service.name")
    description = serializers.CharField(read_only=True, source="service.description")
    icon = serializers.ImageField(read_only=True, source="service.icon")

    class Meta:
        model = FarmerService
        fields = ["id", "name", "description", "icon", "link",]

    def get_service_link(self, obj):
        refernce_id = obj.refernce_id
        return obj.service.service_url.replace("{{refernce_id}}", refernce_id)


class FarmerSerializer(DynamicModelSerializer):
    """Serializer for the Farmer model."""

    entity_card = EntityCardSerializer(read_only=True)
    submission = SubmissionSerializer(required=False)
    phone = PhoneNumberField(required=False, allow_blank=True, allow_null=True)
    plots = serializers.JSONField(
        source="geo_json", 
        allow_null=True, 
        validators=[validate_geojson_polygon, validate_coordinates], 
        required=False
    )
    province = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    meta_data = serializers.JSONField(allow_null=True, required=False)
    linked_services = serializers.SerializerMethodField(
        method_name="get_linked_services"
    )
    buyer = serializers.CharField(source='buyer.id', default=None)

    class Meta:
        model = Farmer
        fields = "__all__"

    def get_linked_services(self, obj):
        qs = FarmerService.objects.filter(farmer=obj, is_active=True, service__is_available=True).all()
        if qs:
            serializer = ExternalServiceSerializer(instance=qs, many=True)
            return serializer.data
        return []

    def validate_country(self, value):
        if value not in COUNTRY_LIST:
            raise serializers.ValidationError(_("Invalid country."))
        return value
    
    def validate(self, attrs):
        if "province" in attrs and "country" in attrs:
            if attrs["province"] not in COUNTRY_WITH_PROVINCE[attrs["country"]]:
                raise serializers.ValidationError({"province": _("Invalid province.")})
        return super().validate(attrs)

    @transaction.atomic
    def create(self, validated_data):
        """Override the default create."""
        user = utils.get_current_user()
        buyer = validated_data.pop("buyer", None)
        request = self.context.get("request")
        sync_from_trace = request.query_params.get("sync_from_trace", False)
        if sync_from_trace:
            buyer_id = buyer.get('id')
            buyer = Entity.objects.get(id=buyer_id)
        if not user.is_admin:
            buyer = utils.get_current_entity()
        submission_data = validated_data.pop("submission", None)
        instance = super().create(validated_data)
        if submission_data:
            submission = self.fields["submission"].create(submission_data)
            instance.submission = submission
        instance.save()
        if buyer:
            EntityBuyer.objects.create(entity=instance, buyer=buyer, is_default=True)
        return instance

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        # Optionally, remove the original field if it's automatically included
        if 'geo_json' in representation:
            representation.pop('geo_json')

        return representation


class AppFarmerSerializer(serializers.ModelSerializer):
    """Serializer for Farmer model."""

    id = SerializableRelatedField(read_only=True)
    name = serializers.CharField(required=False)
    phone = PhoneNumberField(required=False, allow_blank=True)

    class Meta:
        model = Farmer
        fields = (
            "id",
            "name",
            "house_name",
            "phone",
            "street",
            "city",
            "sub_province",
            "province",
            "country",
            "consent_status"
        )

    def to_representation(self, instance):
        """To perform function to_representation."""
        request = self.context.get("request")
        language = request.headers.get("Language", "en")
        data = super(AppFarmerSerializer, self).to_representation(instance)
        data["transaction_details"] = instance.transaction_count(language)
        return data


class OpenTransactionPremiumSerializer(serializers.ModelSerializer):
    id = SerializableRelatedField(read_only=True)
    amount = serializers.FloatField(read_only=True)
    premium = PremiumSerializer(read_only=True)

    class Meta:
        model = PaymentTransaction
        fields = ("id", "amount",'premium',)

class OpenTransactionSerializer(serializers.ModelSerializer):
    """Serializer for creating external transaction as well as getting
    details."""

    quantity = RoundingDecimalField(max_digits=25, decimal_places=3, write_only=True)
    unit = serializers.IntegerField(write_only=True)
    product = ProductSerializer(required=False)
    id = SerializableRelatedField(read_only=True)
    status = serializers.IntegerField(read_only=True)
    destination_quantity = RoundingDecimalField(
        max_digits=25, decimal_places=3, read_only=True
    )
    method = serializers.CharField(required=False)
    created_on = UnixDateTimeField(required=False)
    date = serializers.DateTimeField(required=False)
    currency = serializers.SerializerMethodField()
    premium = serializers.SerializerMethodField()
    premium_transacton = serializers.SerializerMethodField()

    class Meta:
        model = ProductTransaction
        fields = (
            "id",
            "date",
            "quantity",
            "unit",
            "product",
            "unit",
            "destination",
            "destination_quantity",
            "status",
            "method",
            "created_on",
            "currency",
            "source_quantity",
            "amount",
            "premium",
            "premium_transacton",
        )

    def get_currency(self, instance):
        return instance.currency.code

    def get_premium(self, obj):
        premiums = Premium.objects.filter(premium_payments__transaction=obj)
        return PremiumSerializer(premiums, many=True).data

    def get_premium_transacton(self, obj):
        payments = obj.transaction_payments.filter(premium__isnull=False).all()
        return OpenTransactionPremiumSerializer(payments, many=True).data

    def to_representation(self, instance):
        """Convert the instance to a representation suitable for serialization.

        This method is responsible for converting the given instance to a
        representation that can be serialized and returned in the API response.
        It applies specific formatting and modifications to the data before
        returning it.

        Parameters:
        - instance: The instance to be serialized.

        Returns:
        - dict: The serialized representation of the instance.
        """
        data = super(OpenTransactionSerializer, self).to_representation(instance)
        data["total_premium"] = 0
        data["destination"] = instance.destination.name
        data["date_str"] = _(instance.date.strftime("%d %B, %Y"))
        payment_transactions = instance.transaction_payments.filter(premium__isnull=False).all()
        for payment_transaction in payment_transactions:
            if payment_transaction.amount:
                data["total_premium"] += payment_transaction.amount
        return data


class CompanyMemerSerializer(CompanyMemerMiniSerializer):
    """Serializer for CompanyMember.

    This serializer includes details about the user associated with the
    company member, using a nested UserSerializer.
    """

    user = user_serializers.UserSerializer(
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