from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from base.db import models as abstarct_models
from v1.catalogs.models.product_models import Premium
from v1.forms.models import Submission
from v1.supply_chains import constants as sc_consts
from v1.supply_chains.models import base_models
from v1.supply_chains.validators import (validate_coordinates,
                                         validate_geojson_polygon)
from v1.transactions.models.transaction_models import ProductTransaction


class AbstractFarmerModel(
    abstarct_models.AbstractAddressModel,
    abstarct_models.AbstractNumberedModel,
    abstarct_models.AbstractContactModel,
    base_models.Entity,
):
    """An abstract base model for a company, providing fields for basic company
    information such as address, contact details, and a unique identifier."""

    class Meta:
        abstract = True


class Farmer(AbstractFarmerModel):
    """Represents a farmer entity.

    This model stores information about a farmer, including their first name,
    last name, date of birth, gender, and consent status.

    Attributes:
        identification_no (str): The identification number of the farmer.
        first_name (str): The first name of the farmer.
        last_name (str, optional): The last name of the farmer (optional).
        date_of_birth (date, optional): The date of birth of the farmer
            (optional).
        gender (str, optional): The gender of the farmer (optional).
        consent_status (str): The consent status of the farmer, chosen from
            predefined choices.
    """

    identification_no = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Identification"
    )
    reference_number = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Reference Number"
    )
    first_name = models.CharField(max_length=100, verbose_name="First Name")
    last_name = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Last Name"
    )
    date_of_birth = models.DateField(
        null=True, blank=True, verbose_name=_("Date of Birth")
    )
    gender = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_("Gender")
    )
    consent_status = models.CharField(
        max_length=20,
        choices=sc_consts.FarmerConsentStatus.choices,
        default=sc_consts.FarmerConsentStatus.GRANTED,
        verbose_name=_("Consent Status"),
    )
    submission = models.OneToOneField(
        Submission,
        models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Submission"),
    )
    geo_json = models.JSONField(null=True, blank=True,
                         validators=[validate_geojson_polygon,
                                     validate_coordinates])

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def name(self):
        """Returns the full name of the farmer."""
        return f"{self.first_name} {self.last_name}"

    def transaction_count(self, language):
        """To perform function transaction_count."""
        data = {"volume": 0, "income": 0, "premium": 0}
        transactions = ProductTransaction.objects.filter(is_deleted=False).filter(
            Q(source=self) | Q(destination=self)
        )
        data["count"] = transactions.count()
        for transaction in transactions:
            data["volume"] += float(transaction.quantity)
            data["income"] += transaction.amount
            payment_transactions = transaction.transaction_payments.filter(premium__isnull=False).all()
            for payment_transaction in payment_transactions:
                if payment_transaction.amount:
                    data["premium"] += payment_transaction.amount
        first_transaction = transactions.first()
        data["currency"] = (
            first_transaction.currency.name 
            if first_transaction else ""
            )
        return data
