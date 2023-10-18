"""Constants under the catalogs section are stored here."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class CategoryType(models.IntegerChoices):
    """A class to define integer choices for the 'Category' model's 'type'
    field.

    Choices:
    - ENTITY_DOCUMENT: Represents an entity document with a value of 101.
    """

    ENTITY_DOCUMENT = 101, _("Entity Document")


class PremiumCategory(models.TextChoices):
    """
    A class to define text choices for the 'Premium' model's 'category'
    field.

    Choices:
    - BASE_PREMIUM: Represents a base premium with a value of 'PRE'.
    - TRANSACTION_PREMIUM: Represents a transaction premium with a value of
        'TRA'.
    """

    BASE_PREMIUM = "PRE", _("Premium")
    TRANSACTION_PREMIUM = "TRA", _("Transaction Premium")


class PremiumType(models.TextChoices):
    """
    A class to define text choices for the 'Premium' model's 'type' field.

    Choices:
    - PER_TRANSACTION: Represents a per transaction premium with a value of
        'PTR'.
    - PER_KG: Represents a per kg premium with a value of 'PKG'.
    - PER_UNIT_CURRENCY: Represents a per unit currency premium with a value of
        'PUC'.
    - PER_FARMER: Represents a per farmer premium with a value of 'PFA'.
    """

    PER_TRANSACTION = "PTR", _("Per Transaction")
    PER_KG = "PKG", _("Per KG")
    PER_UNIT_CURRENCY = "PUC", _("Per Unit Currency")
    PER_FARMER = "PFA", _("Per Farmer")


class PremiumActivity(models.TextChoices):
    """
    A class to define text choices for the 'Premium' model's 'activity' field.

    Choices:
    - BUY: Represents a buy activity with a value of 'BUY'.
    - SELL: Represents a sell activity with a value of 'SEL'.
    """

    BUY = "BUY", _("Buy")
    SELL = "SEL", _("Sell")


class PremiumCalculationType(models.TextChoices):
    """
    A class to define text choices for the 'Premium' model's 'calculation_type'
    field.

    Choices:
    - NORMAL: Represents a normal calculation type with a value of 'NOR'.
    - MANUAL: Represents a manual calculation type with a value of 'MAN
    - OPTIONS: Represents an options calculation type with a value of 'OPT'.
    """

    NORMAL = "NOR", _("Normal")
    MANUAL = "MAN", _("Manual")
    OPTIONS = "OPT", _("Options")
