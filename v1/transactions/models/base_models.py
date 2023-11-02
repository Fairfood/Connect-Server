from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .. import constants
from base.db.models import AbstractBaseModel
from base.db.models import AbstractNumberedModel
from base.db.utilities import get_file_path
from v1.catalogs.models.product_models import ConnectCard
from v1.forms.models import Form
from v1.supply_chains.models.base_models import Entity


class BaseTransaction(AbstractBaseModel, AbstractNumberedModel):
    date = models.DateField(default=timezone.now, verbose_name=_("Date"))
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
        models.SET_NULL,
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
    form = models.OneToOneField(
        Form, models.SET_NULL, null=True, blank=True, verbose_name=_("Form")
    )

    def __str__(self):
        return f"{self.source} -> {self.destination} {self.amount}"
