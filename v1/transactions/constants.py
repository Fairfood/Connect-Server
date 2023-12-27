from django.db import models
from django.utils.translation import gettext_lazy as _


INCOMING = "INCOMING"
OUTGOING = "OUTGOING"


class PaymentType(models.TextChoices):
    """A Class to define text choices for the 'Payment' model's 'type' field.

    Choices:
    - TRANSACTION: Represents a transaction payment with a value of 'TRA'.
    - PREMIUM: Represents a premium payment with a value of 'PRE'.
    - TRANSACTION_PREMIUM: Represents a transaction premium payment with a
        value of 'TRP'.
    """

    TRANSACTION = "TRANSACTION", _("Transaction")
    PREMIUM = "PREMIUM", _("Premium")
    TRANSACTION_PREMIUM = "TRANSACTION_PREMIUM", _("Transaction Premium")


class VerificationMethodType(models.TextChoices):
    """A class to define text choices for the 'VerificationMethod' model's
    'type' field.

    Choices:
    - CARD: Represents a card verification method with a value of 'CAR'.
    - INVOICE: Represents an invoice verification method with a value of 'INV'.
    - NONE: Represents a no verification method with a value of 'NON'.
    """

    CARD = "CARD", _("Card")
    INVOICE = "INVOICE", _("Invoice")
    NONE = "NONE", _("None")
