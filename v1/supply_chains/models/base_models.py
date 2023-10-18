from django.db import models
from django.utils.translation import gettext_lazy as _

from .. import constants as company_consts
from base.db.utilities import get_file_path


class AbstarctEntityModel(models.Model):
    """
    Abstract base model for entities in the supply chain system.

    Fields:
    - image (ImageField): An image representing the entity.
    - description (CharField): A short description of the entity.
    - invited_by (ForeignKey): The company that invited the entity to join the
        supply chain.
    - invited_on (DateTimeField): The date and time when the entity was invited
        to join the supply chain.
    - joined_on (DateTimeField): The date and time when the entity joined the
        supply chain.
    - status (IntegerField): The current status of the entity in the supply
        chain.
    - is_verified (BooleanField): Whether the entity has been verified by the
        supply chain system.
    - buyer (ForeignKey): The company that buyying from the entity.
    """

    image = models.ImageField(
        upload_to=get_file_path,
        null=True,
        blank=True,
        verbose_name=_("Photo"),
    )
    description = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name=_("Description"),
    )
    invited_by = models.ForeignKey(
        "supply_chains.Company",
        on_delete=models.SET_NULL,
        related_name="invited_%(class)s",
        null=True,
        blank=True,
        verbose_name=_("Invited By"),
    )
    refferenced_by = models.ForeignKey(
        "accounts.CustomUser",
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        related_name="refered_%(class)ss",
        verbose_name=_("Referenced By"),
    )
    invited_on = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Invited Date")
    )
    joined_on = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Joining Date")
    )
    status = models.CharField(
        max_length=3,
        default=company_consts.EntityStatus.INACTIVE,
        choices=company_consts.EntityStatus.choices,
        verbose_name=_("Company Current Status"),
    )
    is_verified = models.BooleanField(
        default=False, verbose_name=_("Is Entity Verified")
    )
    buyer = models.ForeignKey(
        "supply_chains.Company",
        on_delete=models.SET_NULL,
        related_name="%(class)s_supplers",
        null=True,
        blank=True,
        verbose_name=_("Buyer"),
    )

    class Meta:
        """Meta class for the above model."""

        abstract = True
