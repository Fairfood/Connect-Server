from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from hashid_field import HashidField

from base.db.models import AbstarctAditionalField
from base.db.models import AbstractBaseModel
from base.db.models import AbstractNumberedModel
from base.db.utilities import get_file_path
from v1.catalogs.models.common_models import Currency
from v1.catalogs.models.product_models import ConnectCard
from v1.catalogs.models.product_models import Product
from v1.supply_chains.models.company_models import Company
from v1.transactions import constants


class BatchTransaction(AbstractBaseModel, AbstractNumberedModel):
    """
    Represents batch transactions between farmer/company and a destination
    destination company.

    Attributes:
        parents (ManyToManyField): Parent transactions related to the current
            transaction.
        destination (ForeignKey to Company): The destination company for the
            transaction.
        source_type (ForeignKey to ContentType): The content type of the source
            (either a company or a farmer).
        source_id (HashidAutoField): Identifier of the source.
        source (GenericForeignKey): A generic foreign key linking to either a
            Company or a Farmer model.
        date (DateTimeField): Date and time of the transaction.
        invoice_number (CharField): Invoice number for the transaction.
        invoice (FileField): An uploaded invoice file.
        card (ForeignKey to ConnectCard): A ConnectCard associated with the
            transaction.
        quality_correction (FloatField): Quality correction value.
        deleted (BooleanField): Indicates if the transaction is deleted.
        product (ForeignKey to Product): The associated product.
        quantity (DecimalField): The quantity of the transaction.
        verification_method (IntegerField): Verification method used in the
            transaction.
        price (FloatField): Price associated with the transaction.
        currency (ForeignKey to Currency): The currency used in the
            transaction.
        verification_latitude (FloatField): Latitude of the verification
            location.
        verification_longitude (FloatField): Longitude of the verification
            location.
    """

    parents = models.ManyToManyField(
        "self",
        related_name="children",
        symmetrical=False,
        blank=True,
        verbose_name=_("Parent Transactions"),
    )
    destination = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="incoming_transactions",
        verbose_name=_("Destination"),
    )

    # source can be a company or a farmer
    source_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        verbose_name=_("Source Type"),
        limit_choices_to={"model__in": ["company", "farmer"]},
    )
    source_id = HashidField(verbose_name=_("Source ID"))
    source = GenericForeignKey(
        "source_type",
        "source_id",
    )

    date = models.DateTimeField(default=timezone.now, verbose_name=_("Date"))
    invoice_number = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("Invoice Number")
    )
    invoice = models.FileField(
        upload_to=get_file_path,
        null=True,
        blank=True,
        verbose_name=_("Invoice"),
    )
    card = models.ForeignKey(
        ConnectCard,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Card"),
    )
    quality_correction = models.FloatField(
        default=100.00, verbose_name=_("Quality Correction")
    )

    deleted = models.BooleanField(default=False, verbose_name=_("Deleted"))
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, verbose_name=_("Product")
    )

    quantity = models.DecimalField(
        default=0.0,
        max_digits=25,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name=_("Quantity"),
    )
    verification_method = models.IntegerField(
        default=constants.VerificationMethodType.NONE,
        choices=constants.VerificationMethodType.choices,
        verbose_name=_("Verification Method"),
    )
    price = models.FloatField(
        default=0, null=True, blank=True, verbose_name=_("Price")
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Currency"),
    )
    verification_latitude = models.FloatField(
        default=0.0, verbose_name=_("Verification Latitude")
    )
    verification_longitude = models.FloatField(
        default=0.0, verbose_name=_("Verification Longitude")
    )

    def __str__(self):
        return f"{self.number}: {self.source} -> {self.destination}"

    def source_poducts(self):
        """
        Returns a queryset of products associated with the source of the
        transaction.
        """
        product_ids = self.parents.values_list("product", flat=True)
        return Product.objects.filter(id__in=product_ids)

    def source_quantity(self):
        """
        Returns the total quantity of products associated with the source of
        the transaction.
        """
        return self.parents.aggregate(models.Sum("quantity"))["quantity__sum"]


class BatchTransactionAdditionalFields(AbstarctAditionalField):
    """
    Represents additional fields associated with a batch transaction.

    Attributes:
    - transation (ForeignKey): The transaction associated with the additional
        field.
    """

    transation = models.ForeignKey(
        BatchTransaction,
        on_delete=models.CASCADE,
        related_name="additional_fields",
        verbose_name=_("Transaction"),
    )

    def __str__(self):
        return f"{self.field}: {self.value}"
