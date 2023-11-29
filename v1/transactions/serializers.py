from django.db import transaction
from rest_framework import serializers

from base.authentication import utilities as utils
from base.drf import fields
from base.drf.fields import SerializableRelatedField
from base.drf.serializers import DynamicModelSerializer
from v1.catalogs.models.common_models import Currency
from v1.catalogs.serializers.currency import CurrencySerializer
from v1.catalogs.serializers.products import ConnectCardSerializer
from v1.catalogs.serializers.products import PremiumSerializer
from v1.forms.serializers import SubmissionSerializer
from v1.transactions import constants
from v1.transactions.models.payment_models import PaymentTransaction
from v1.transactions.models.transaction_models import ProductTransaction


class PaymentTransactionsSerializer(DynamicModelSerializer):
    """Serializer for PaymentTransactionsSerializer."""

    premium_details = PremiumSerializer(source="premium", read_only=True)
    currency_details = CurrencySerializer(source="currency", read_only=True)
    type = serializers.SerializerMethodField()

    class Meta:
        """Meta class."""

        model = PaymentTransaction
        fields = "__all__"

    def get_type(self, obj):
        """Get type."""
        entity = utils.get_current_entity()
        return (
            constants.OUTGOING
            if obj.source.id == entity.id
            else constants.INCOMING
        )


class ProductTransactionSerializer(DynamicModelSerializer):
    """Serializer for ProductTransactionSerializer."""

    transaction_payments = PaymentTransactionsSerializer(
        many=True,
        fields=("id", "premium", "selected_option", "amount", "payment_type"),
        required=False,
    )
    amount = fields.RoundingDecimalField(
        max_digits=10, decimal_places=3, write_only=True
    )
    currency = SerializableRelatedField(
        queryset=Currency.objects.all(), write_only=True
    )
    type = serializers.SerializerMethodField()
    source_quantity = fields.RoundingDecimalField(
        max_digits=10, decimal_places=3, read_only=True
    )
    current_quantity = fields.RoundingDecimalField(
        max_digits=10, decimal_places=3, read_only=True
    )
    submissions = SubmissionSerializer(many=True, required=False)
    card_details = ConnectCardSerializer(source="card", read_only=True)

    class Meta:
        """Meta class."""

        model = ProductTransaction
        fields = "__all__"

    def validate(self, data):
        """Validate parents."""
        entity = utils.get_current_entity()
        source = data.get("source", None)
        if source and source == entity:
            self._check_parents(data)
        return data

    @transaction.atomic
    def create(self, validated_data):
        """Create method."""
        payments = validated_data.pop("transaction_payments", [])
        currency = validated_data.pop("currency")
        amount = validated_data.pop("amount")
        submissions = validated_data.pop("submissions", [])
        instance = super().create(validated_data)
        self._create_payments(
            payments, instance, amount=amount, currency=currency
        )
        submission_objs = self.fields["submissions"].create(submissions)
        instance.submissions.add(*submission_objs)
        return instance

    def get_type(self, obj):
        """Get type."""
        entity = utils.get_current_entity()
        return (
            constants.OUTGOING
            if obj.source.id == entity.id
            else constants.INCOMING
        )

    def _create_payments(self, payments, instance, **kwargs):
        """Create payments."""
        for payment in payments:
            PaymentTransaction.objects.create(
                **payment,
                transaction=instance,
                currency=kwargs.get("currency"),
            )
        PaymentTransaction.objects.create(
            transaction=instance,
            currency=kwargs.get("currency"),
            amount=kwargs.get("amount"),
            payment_type=constants.PaymentType.TRANSACTION,
        )

    def _check_parents(data):
        """Check parents."""
        parents = data.get("parents", None)
        if not parents:
            raise serializers.ValidationError(
                {"parents": "This field is required for sending."}
            )
        for parent in parents:
            if parent.destination != data["source"]:
                raise serializers.ValidationError(
                    {
                        "parents": (
                            f"parent batch {parent.number} not "
                            f"belongs to {data['source']}"
                        )
                    }
                )
