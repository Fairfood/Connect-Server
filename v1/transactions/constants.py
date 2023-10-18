from django.db import models
from django.utils.translation import gettext_lazy as _


class PaymentType(models.TextChoices):
    """
    A Class to define text choices for the 'Payment' model's 'type' field.

    Choices:
    - TRANSACTION: Represents a transaction payment with a value of 'TRA'.
    - PREMIUM: Represents a premium payment with a value of 'PRE'.
    - TRANSACTION_PREMIUM: Represents a transaction premium payment with a
        value of 'TRP'.
    """

    TRANSACTION = "TRA", _("Transaction")
    PREMIUM = "PRE", _("Premium")
    TRANSACTION_PREMIUM = "TRP", _("Transaction Premium")


class VerificationMethodType(models.TextChoices):
    """
    A class to define text choices for the 'VerificationMethod' model's 'type'
    field.

    Choices:
    - CARD: Represents a card verification method with a value of 'CAR'.
    - INVOICE: Represents an invoice verification method with a value of 'INV'.
    - NONE: Represents a no verification method with a value of 'NON'.
    """

    CARD = "CAR", _("Card")
    INVOICE = "INV", _("Invoice")
    NONE = "NON", _("None")
