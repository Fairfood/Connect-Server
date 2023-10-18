from django.db import models
from django.utils.translation import gettext_lazy as _

from .. import constants
from base.db.models import AbstarctAditionalField
from base.db.models import AbstractBaseModel
from base.db.utilities import get_file_path
from v1.catalogs.models.common_models import Currency
from v1.catalogs.models.product_models import ConnectCard
from v1.catalogs.models.product_models import Premium
from v1.catalogs.models.product_models import PremiumOption
from v1.supply_chains.models.company_models import Company
from v1.supply_chains.models.farmer_models import Farmer
from v1.transactions.models.transaction_models import BatchTransaction


class AbstarctPayment(AbstractBaseModel):
    """
    An abstract model representing various payment types in the system.

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
        max_length=3,
        choices=constants.PaymentType.choices,
        default=constants.PaymentType.TRANSACTION,
        verbose_name=_("Payment Type"),
    )
    source = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="%(class)s",
        null=True,
        blank=True,
        verbose_name=_("Source"),
    )
    premium = models.ForeignKey(
        Premium,
        on_delete=models.PROTECT,
        related_name="%(class)s_premium_payments",
        null=True,
        blank=True,
        verbose_name=_("Premium"),
    )
    card = models.ForeignKey(
        ConnectCard,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Card"),
    )
    invoice = models.FileField(
        upload_to=get_file_path,
        null=True,
        blank=True,
        verbose_name=_("Invoice"),
    )
    invoice_number = models.CharField(
        max_length=100, null=True, blank=True, verbose_name=_("Invoice Number")
    )
    amount = models.FloatField(default=0.0, verbose_name=_("Amount"))
    selected_option = models.ForeignKey(
        PremiumOption,
        on_delete=models.SET_NULL,
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
        BatchTransaction,
        on_delete=models.CASCADE,
        related_name="%(class)s_transaction_payments",
        null=True,
        blank=True,
    )
    verification_latitude = models.FloatField(
        default=0.0, verbose_name=_("Verification Latitude")
    )
    verification_longitude = models.FloatField(
        default=0.0, verbose_name=_("Verification Longitude")
    )

    method = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        choices=constants.VerificationMethodType.choices,
    )

    class Meta:
        abstract = True

    def save(self, **kwargs):
        """save() override to pre and post save functions."""
        # self._update_from_transaction()
        self._update_payment_status()
        self._update_verification_method()
        super().save(**kwargs)

    def _update_payment_status(self):
        """To update payment_status with available relations."""
        if self.transaction and self.premium:
            self.payment_type = constants.TRANSACTION_PREMIUM
        else:
            if self.transaction:
                self.payment_type = constants.BASE_TRANSACTION
            elif self.premium:
                self.payment_type = constants.BASE_PREMIUM
            else:
                raise Exception("Payment type can not determined.")

    def _update_verification_method(self):
        """Update verification method card/receipt."""
        if self.card:
            self.method = constants.CARD_VERIFICATION
        elif self.invoice:
            self.method = constants.INVOICE_VERIFICATION
        else:
            self.method = constants.NO_VERIFICATION


class FarmerPayment(AbstarctPayment):
    """
    Represents a payment from a source entity to a farmer.

    This model captures payments made from a source entity (e.g., a company)
    to a farmer. It extends the abstract payment model and includes additional
    attributes to specify the destination farmer.

    Attributes:
    - destination (Farmer): The farmer who is the recipient of the payment.

    Note:
    This model inherits attributes and functionality from the abstract payment
    model (AbstarctPayment) and extends it to include the destination farmer
    associated with the payment.
    """

    destination = models.ForeignKey(
        Farmer,
        on_delete=models.CASCADE,
        related_name="from_payments",
        verbose_name=_("Destination"),
    )

    def __str__(self):
        return f"{self.source.name} -> {self.destination.name}"


class CompanyPayment(AbstarctPayment):
    """
    Represents a payment from a source entity to a company.

    This model captures payments made from a source entity (e.g., a company) to
    another company. It extends the abstract payment model and includes
    additional attributes to specify the destination company.

    Attributes:
    - destination (Company): The company that is the recipient of the payment.

    Note:
    This model inherits attributes and functionality from the abstract payment
    model (AbstarctPayment) and extends it to include the destination company
    associated with the payment.
    """

    destination = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="from_payments",
        verbose_name=_("Destination"),
    )

    def __str__(self):
        return f"{self.source.name} -> {self.destination.name}"


class FarmerPaymentAditionalField(AbstarctAditionalField):
    """
    Represents an additional field associated with a farmer payment.

    This model captures additional fields associated with a farmer payment.
    It extends the abstract payment additional field model
    (AbstarctPaymentAditionalField) and includes a foreign key reference to the
    associated farmer payment.

    Attributes:
    - payment (FarmerPayment): The farmer payment to which this additional
        field is associated.

    Note:
    This model inherits attributes and functionality from the abstract payment
    additional field model (AbstarctPaymentAditionalField) and extends it to
    include the farmer payment to which this additional field belongs.
    """

    payment = models.ForeignKey(
        FarmerPayment,
        on_delete=models.CASCADE,
        related_name="additional_fields",
        verbose_name=_("Payment"),
    )

    def __str__(self):
        return f"{self.field.name} -> {self.value}"


class CompanyPaymentAditionalField(AbstarctAditionalField):
    """
    Represents an additional field associated with a company payment.

    This model captures additional fields associated with a company payment. It
    includes a foreign key reference to the associated company payment.

    Attributes:
    - payment (CompanyPayment): The company payment to which this additional
      field is associated.

    Note:
    This model is used to store additional fields related to a company payment
    and is linked to the company payment it belongs to.

    """

    payment = models.ForeignKey(
        CompanyPayment,
        on_delete=models.CASCADE,
        related_name="additional_fields",
        verbose_name=_("Payment"),
    )

    def __str__(self):
        return f"{self.field.name} -> {self.value}"
