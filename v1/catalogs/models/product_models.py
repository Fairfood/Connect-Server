from django.db import models
from django.utils.translation import gettext_lazy as _

from .. import constants
from base.db.models import AbstractBaseModel
from base.db.utilities import get_file_path


class Product(AbstractBaseModel):
    """Model representing a product entity.

    This model is used to represent a product entity within the system. It
    contains fields for the product's name, description, and default currency.

    Attributes:
        name (str): The name of the product.
        description (str): The description of the product.
        image (ImageField): The image of the product.
    """

    name = models.CharField(
        max_length=500,
        verbose_name=_("Product Name"),
    )
    description = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name=_("Product Description"),
    )
    image = models.ImageField(
        upload_to=get_file_path,
        null=True,
        blank=True,
        verbose_name=_("Product Image"),
    )

    def __str__(self):
        """Function to return value in django admin."""
        return f"{self.name}"


class ConnectCard(AbstractBaseModel):
    """Model representing a connect card entity.

    This model is used to represent a connect card entity within the system. It
    contains fields for the connect card's display id and card id.

    Attributes:
        display_id (str): The display id of the connect card.
        card_id (str): The card id of the connect card.
    """

    display_id = models.CharField(
        max_length=100, null=True, blank=True, verbose_name=_("Display ID")
    )
    card_id = models.CharField(
        max_length=100, null=True, blank=True, verbose_name=_("Card ID")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    def __str__(self):
        """Function to return value in django admin."""
        return f"{self.display_id} - {self.card_id}"


class Premium(AbstractBaseModel):
    """Represents a premium category or type associated with a supply chain.

    Attributes:
        category (str): The category of the premium, chosen from available
            choices.
        name (str): The name of the premium.
        owner (Company): The company that owns or manages the premium.
        type (str): The type of the premium, such as per unit or
            currency-based.
        amount (float): The amount associated with the premium, if applicable.
        included (bool): Indicates whether the premium is included in
            activities.
        dependant_on_card (bool): Indicates whether the premium depends on a
            card.
        applicable_activity (str): The activity to which the premium is
            applicable.
        calculation_type (str): The method of calculating the premium.
        is_active (bool): Indicates whether the premium is currently active in
            the supply chain.
    """

    category = models.CharField(
        max_length=11,
        choices=constants.PremiumCategory.choices,
        default=constants.PremiumCategory.TRANSACTION,
        verbose_name=_("Premium Category"),
    )
    name = models.CharField(max_length=100, verbose_name=_("Premium Name"))
    label = models.CharField(
        max_length=100, null=True, blank=True, verbose_name=_("Label")
    )
    owner = models.ForeignKey(
        "supply_chains.Company",
        on_delete=models.CASCADE,
        related_name="owned_premiums",
        null=True,
        blank=True,
        verbose_name=_("Owner"),
    )
    type = models.CharField(
        max_length=17,
        default=constants.PremiumType.PER_UNIT_CURRENCY,
        choices=constants.PremiumType.choices,
        verbose_name=_("Premium Type"),
    )
    amount = models.FloatField(
        default=0.0, null=True, blank=True, verbose_name=_("Amount")
    )
    included = models.BooleanField(default=True, verbose_name=_("Included"))
    dependant_on_card = models.BooleanField(
        default=False, verbose_name=_("Dependant on Card")
    )
    applicable_activity = models.CharField(
        max_length=4,
        default=constants.PremiumActivity.BUY,
        choices=constants.PremiumActivity.choices,
        verbose_name=_("Applicable Activity"),
    )
    calculation_type = models.CharField(
        max_length=7,
        default=constants.PremiumCalculationType.NORMAL,
        choices=constants.PremiumCalculationType.choices,
        verbose_name=_("Calculation Type"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    def __str__(self):
        return f"{self.name} - {self.owner.name}"


class PremiumOption(AbstractBaseModel):
    """Represents a premium slab for a project's premium.

    Attributes:
        premium (ForeignKey): The project premium associated with the slab.
        name (str): Name showing in the drop-down.
        amount (float): The amount for the premium slab.

    # TODO: Write an example (Moisture Premium.)
    """

    premium = models.ForeignKey(
        Premium,
        on_delete=models.CASCADE,
        related_name="options",
        verbose_name=_("Premium"),
    )
    name = models.CharField(max_length=25, verbose_name=_("Option Name"))
    amount = models.FloatField(verbose_name=_("Amount"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    def __str__(self):
        return f"{self.premium.name} : {self.name} : {self.amount}"


class PremiumRange(AbstractBaseModel):
    """Represents a premium range for a project's premium.

    Attributes:
        premium (ForeignKey): The project premium associated with the range.
        range_from (float): The range from value.
        range_to (float): The range to value.
        amount (float): The amount for the premium range.
    """

    premium = models.ForeignKey(
        Premium,
        on_delete=models.CASCADE,
        related_name="ranges",
        verbose_name=_("Premium"),
    )
    range_from = models.FloatField(verbose_name=_("Range From"))
    range_to = models.FloatField(verbose_name=_("Range To"))
    amount = models.FloatField(verbose_name=_("Amount"))

    def __str__(self):
        return (
            f"{self.premium.name} : {self.range_from}"
            f" - {self.range_to} : {self.amount}"
        )
