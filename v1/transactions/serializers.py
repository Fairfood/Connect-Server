from rest_framework import serializers

from base.drf.fields import SerializableRelatedField
from base.drf.serializers import DynamicModelSerializer
from v1.catalogs.models.common_models import Currency
from v1.catalogs.serializers.currency import CurrencySerializer
from v1.catalogs.serializers.products import PremiumSerializer
from v1.transactions import constants
from v1.transactions.models.payment_models import PaymentTransaction
from v1.transactions.models.transaction_models import ProductTransaction


class PaymentTransactionsSerializer(DynamicModelSerializer):
    """Serializer for PaymentTransactionsSerializer."""

    premium_details = PremiumSerializer(source="premium", read_only=True)
    currency_details = CurrencySerializer(source="currency", read_only=True)

    class Meta:
        """Meta class."""

        model = PaymentTransaction
        fields = "__all__"


class ProductTransactionSerializer(DynamicModelSerializer):
    """Serializer for ProductTransactionSerializer."""

    transaction_payments = PaymentTransactionsSerializer(
        many=True, fields=("id", "premium", "selected_option", "amount")
    )
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = SerializableRelatedField(queryset=Currency.objects.all())
    source_quantity = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    current_quantity = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        """Meta class."""

        model = ProductTransaction
        fields = "__all__"

    def create(self, validated_data):
        """Create method."""
        payments = validated_data.pop("transaction_payments")
        currency = validated_data.pop("currency")
        amount = validated_data.pop("amount")
        instance = super().create(validated_data)
        self._create_premiums(
            payments, instance, amount=amount, currency=currency
        )
        return super().create(validated_data)

    def _create_payments(self, payments, instance, **kwargs):
        """Create payments."""
        for payment in payments:
            PaymentTransaction.objects.create(
                **payment,
                transaction=instance,
                currency=kwargs.get("currency")
            )
        PaymentTransaction.objects.create(
            transaction=instance,
            currency=kwargs.get("currency"),
            amount=kwargs.get("amount"),
            payment_type=constants.PaymentType.TRANSACTION,
        )
