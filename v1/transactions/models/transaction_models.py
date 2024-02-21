from django.db import models
from django.utils.translation import gettext_lazy as _

from v1.catalogs.models.product_models import Product
from v1.transactions import constants
from v1.transactions.models.base_models import BaseTransaction


class ProductTransaction(BaseTransaction):
    """Represents batch transactions between farmer/company and a destination
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
    quality_correction = models.FloatField(
        default=100.00, verbose_name=_("Quality Correction")
    )

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

    def __str__(self):
        return f"{self.number}: {self.source} -> {self.destination}"

    def save(self, *args, **kwargs):
        """Save method for the model.

        This method updates the verification method before calling the
        parent class's save method.
        """
        self._update_verification_method()
        super().save(*args, **kwargs)

    def base_payment(self):
        """Base payment without any premium."""
        return self.transaction_payments.filter(
            payment_type=constants.PaymentType.TRANSACTION
        ).first()

    @property
    def amount(self):
        """
        Returns the total amount of the transaction.
        """
        return self.base_payment().amount

    @property
    def currency(self):
        """
        Returns the currency of the transaction.
        """
        return self.base_payment().currency

    def source_poducts(self):
        """Returns a queryset of products associated with the source of the
        transaction."""
        product_ids = self.parents.values_list("product", flat=True)
        return Product.objects.filter(id__in=product_ids)

    @property
    def source_quantity(self):
        """Returns the total quantity of products associated with the source of
        the transaction."""
        source_quantity = self.parents.aggregate(models.Sum("quantity"))[
            "quantity__sum"
        ]
        return source_quantity or self.quantity

    @property
    def current_quantity(self):
        """Returns the balence quantity of products associated with the source
        of the transaction."""
        return 0 if self.children.exists() else self.quantity

    def _update_verification_method(self):
        """Update verification method card/receipt."""
        if self.card:
            self.method = constants.VerificationMethodType.CARD
        elif self.invoice:
            self.method = constants.VerificationMethodType.INVOICE
        else:
            self.method = constants.VerificationMethodType.NONE
