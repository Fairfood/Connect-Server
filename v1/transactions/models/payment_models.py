from django.db import models
from django.utils.translation import gettext_lazy as _

from .. import constants
from v1.catalogs.models.common_models import Currency
from v1.catalogs.models.product_models import Premium
from v1.transactions.models.base_models import BaseTransaction
from v1.transactions.models.transaction_models import ProductTransaction


class PaymentTransaction(BaseTransaction):
    """An abstract model representing various payment types in the system.

    Attributes:
    - payment_type (str): The type of payment, e.g., 'Transaction', 'Premium'.
    - source (Company): The source company from which the payment originates.
    - premium (Premium): The premium associated with the payment,
        if applicable.
    - card (ConnectCard): The card used for the payment, if any.
    - invoice (FileField): An uploaded invoice document, if available.
    - invoice_number (str): The invoice number associated with the payment.
    - amount (float): The payment amount.
    - selected_option (PremiumOption): The selected premium option,
        if applicable.
    - currency (Currency): The currency used for the payment.
    - verification_latitude (float): The latitude for verification purposes.
    - verification_longitude (float): The longitude for verification purposes.
    - method (str): The verification method type, e.g., 'GPS', 'QR Code', etc.

    Note:
    This is an abstract model that serves as the base for various
    payment-related models. Concrete models should inherit from this abstract
    model and add any additional fields or methods as needed.
    """

    payment_type = models.CharField(
        max_length=20,
        choices=constants.PaymentType.choices,
        default=constants.PaymentType.TRANSACTION_PREMIUM,
        verbose_name=_("Payment Type"),
    )
    premium = models.ForeignKey(
        Premium,
        on_delete=models.PROTECT,
        related_name="premium_payments",
        null=True,
        blank=True,
        verbose_name=_("Premium"),
    )
    amount = models.FloatField(default=0.0, verbose_name=_("Amount"))
    selected_option = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("Selected Option"),
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Currency"),
    )
    transaction = models.ForeignKey(
        ProductTransaction,
        on_delete=models.CASCADE,
        related_name="transaction_payments",
        null=True,
        blank=True,
    )
    comment = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Comment"),
    )

    def save(self, **kwargs):
        """save() override to pre and post save functions."""
        self._update_from_transaction()
        self._update_payment_status()
        self._update_verification_method()
        super().save(**kwargs)

    def _update_from_transaction(self):
        """To update payment_from and payment_to from the available
        transaction."""
        if self.transaction:
            self.source = self.transaction.destination
            self.destination = self.transaction.source
            self.date = self.transaction.date
            self.created_on = self.transaction.created_on

            # invoice will get from transaction if not available.
            if not self.invoice:
                self.invoice = self.transaction.invoice
            self.card = self.transaction.card
            self.invoice_number = self.transaction.invoice_number

            # getting verification lat-long
            lat = self.transaction.verification_latitude
            lon = self.transaction.verification_longitude
            self.verification_latitude = lat
            self.verification_longitude = lon

    def _update_payment_status(self):
        """To update payment_status with available relations."""
        if self.transaction and self.premium:
            self.payment_type = constants.PaymentType.TRANSACTION_PREMIUM
        else:
            if self.transaction:
                self.payment_type = constants.PaymentType.TRANSACTION
            elif self.premium:
                self.payment_type = constants.PaymentType.PREMIUM
            else:
                raise Exception("Payment type can not determined.")

    def _update_verification_method(self):
        """Update verification method card/receipt."""
        if self.card:
            self.method = constants.VerificationMethodType.CARD
        elif self.invoice:
            self.method = constants.VerificationMethodType.INVOICE
        else:
            self.method = constants.VerificationMethodType.NONE
