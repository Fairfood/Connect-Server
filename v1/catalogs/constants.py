from django.db import models
from django.utils.translation import gettext_lazy as _


class PremiumCategory(models.TextChoices):
    """A class to define text choices for the 'Premium' model's 'category'
    field.

    Choices:
    - PAYOUT: Represents a payout premium. (Payment without Transaction)
            example: Yearly Bonus.
    - TRANSACTION: Represents a transaction premium with a value
    """

    PAYOUT = "PAYOUT", _("Payout Premium")
    TRANSACTION = "TRANSACTION", _("Transaction Premium")


class PremiumType(models.TextChoices):
    """A class to define text choices for the 'Premium' model's 'type' field.

    Choices:
    - PER_TRANSACTION: Represents a per transaction premium with a value of
        'PTR'.
    - PER_KG: Represents a per kg premium with a value of 'PKG'.
    - PER_UNIT_CURRENCY: Represents a per unit currency premium with a value of
        'PUC'.
    - PER_FARMER: Represents a per farmer premium with a value of 'PFA'.
    """

    PER_TRANSACTION = "PER_TRANSACTION", _("Per Transaction")
    PER_KG = "PER_KG", _("Per KG")
    PER_UNIT_CURRENCY = "PER_UNIT_CURRENCY", _("Per Unit Currency")
    PER_FARMER = "PER_FARMER", _("Per Farmer")


class PremiumActivity(models.TextChoices):
    """A class to define text choices for the 'Premium' model's 'activity'
    field.

    Choices:
    - BUY: Represents a buy activity with a value of 'BUY'.
    - SELL: Represents a sell activity with a value of 'SEL'.
    """

    BUY = "BUY", _("Buy")
    SELL = "SELL", _("Sell")


class PremiumCalculationType(models.TextChoices):
    """A class to define text choices for the 'Premium' model's
    'calculation_type' field.

    Choices:
    - NORMAL: Represents a normal calculation type with a value of 'NOR'.
    - MANUAL: Represents a manual calculation type with a value of 'MAN
    - OPTIONS: Represents an options calculation type with a value of 'OPT'.
    - RANGE: Represents a range calculation type with a value of 'RAN'.
    """

    NORMAL = "NORMAL", _("Normal")
    MANUAL = "MANUAL", _("Manual")
    OPTIONS = "OPTIONS", _("Options")
    RANGE = "RANGE", _("Range")
