from django.db import models
from django.utils.translation import gettext_lazy as _

from . import base_models
from .. import constants as sc_consts
from base.db import models as abstarct_models
from v1.forms.models import Submission


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

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def name(self):
        """Returns the full name of the farmer."""
        return f"{self.first_name} {self.last_name}"
