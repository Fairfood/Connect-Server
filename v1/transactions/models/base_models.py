from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .. import constants
from base.db.models import AbstractBaseModel
from base.db.models import AbstractNumberedModel
from base.db.utilities import get_file_path
from v1.catalogs.models.product_models import ConnectCard
from v1.forms.models import Submission
from v1.supply_chains.models.base_models import Entity


class BaseTransaction(AbstractBaseModel, AbstractNumberedModel):
    """Base model for generic transactions, not specifically tied to finances.

    Attributes:
        created_on (datetime): Timestamp of transaction creation.
        date (datetime): Date and time of the transaction.
        source (Entity): Entity initiating the transaction.
        destination (Entity): Entity receiving the transaction.
        card (ConnectCard): Associated connect card (optional).
        invoice (FileField): Invoice file (optional).
        invoice_number (str): Invoice number (optional).
        verification_latitude (float): Latitude of verification location.
        verification_longitude (float): Longitude of verification location.
        method (str): Verification method used (optional).
        submissions (ManyToManyField): Related submissions.
    """

    created_on = models.DateTimeField(
        default=timezone.now, verbose_name=_("Created On")
    )
    date = models.DateTimeField(default=timezone.now, verbose_name=_("Date"))
    source = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name="outgoing_transactions",
        verbose_name=_("Source"),
    )
    destination = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name="incoming_transactions",
        verbose_name=_("Destination"),
    )
    card = models.ForeignKey(
        ConnectCard,
        on_delete=models.SET_NULL,
        related_name="transactions",
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
    submissions = models.ManyToManyField(
        Submission, blank=True, verbose_name=_("Submissions")
    )

    def __str__(self):
        return f"{self.source} -> {self.destination}"
