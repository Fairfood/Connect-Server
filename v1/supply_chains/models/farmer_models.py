from datetime import datetime

from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from pyexpat import model

from base.db import models as abstarct_models
from base.db.models import AbstractBaseModel
from base.db.utilities import get_file_path
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
        reference_number (str): Used to mention external reference of a farmer.
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
    geo_json = models.JSONField(
        null=True,
        blank=True,
        validators=[validate_geojson_polygon, validate_coordinates],
    )
    meta_data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        """
        Override save to prevent saving last name as None when changing 
        consent through djadmin.
        """
        if self.last_name is None:
            self.last_name = ''
        super().save(*args, **kwargs)

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
            payment_transactions = transaction.transaction_payments.filter(
                premium__isnull=False
            ).all()
            for payment_transaction in payment_transactions:
                if payment_transaction.amount:
                    data["premium"] += payment_transaction.amount
        first_transaction = transactions.first()
        data["currency"] = first_transaction.currency.code \
            if first_transaction else ""
        return data


class ExternalService(AbstractBaseModel):
    """
    Represents an external service that can be associated with a farmer.

    Attributes:
        name (str): The name of the external service.
        description (str): A detailed description of the service.
        icon (ImageField): An optional icon/image representing the service, stored using a custom file path.
        service_url (str): A URL for the service; can have variable schema types and potentially replaceable characters.
        is_available (bool): Indicates whether the service is currently available.
    """

    name = models.CharField(max_length=255, help_text="Name of the external service.")
    description = models.TextField(help_text="Detailed description of the service.")
    icon = models.ImageField(
        upload_to=get_file_path,
        null=True,
        blank=True,
        verbose_name=_("Service Icon"),
        help_text="Optional icon/image to represent the service.",
    )
    service_url = models.TextField(
        help_text=(
            "URL of the external service. "
            "Can have variable schema types and lengths. "
            "May contain replaceable characters for dynamic URLs. "
            "Should contain a {{refernce_id}} for replacing farmer refernce id."
        )
    )
    is_available = models.BooleanField(
        default=True, help_text="Indicates if the service is currently available."
    )

    def __str__(self):
        return self.name


class FarmerService(AbstractBaseModel):
    """
    Represents the relationship between a farmer and an external service.

    Attributes:
        farmer (ForeignKey): The farmer associated with the service.
        service (ForeignKey): The external service linked to the farmer.
        reference_id (str): An identifier to track the farmer's association with the service.
        is_active (bool): Indicates if the service is active for the farmer.
    """

    farmer = models.ForeignKey(
        Farmer,
        on_delete=models.CASCADE,
        related_name="services",
        help_text="The farmer who is associated with this service.",
    )
    service = models.ForeignKey(
        ExternalService,
        on_delete=models.CASCADE,
        related_name="farmers",
        help_text="The external service associated with the farmer.",
    )
    refernce_id = models.CharField(
        max_length=100,
        help_text="A unique identifier for the farmer's association with the service.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates if this service is currently active for the farmer.",
    )

    def __str__(self):
        return f"{self.farmer} - {self.service}"

    def save(self, *args, **kwargs):
        farm_service = super().save(*args, **kwargs)
        self.farmer.updated_on = datetime.now()
        self.farmer.save()
        return farm_service
