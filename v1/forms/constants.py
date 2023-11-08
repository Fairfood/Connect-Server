from django.db import models
from django.utils.translation import gettext_lazy as _


class FormType(models.TextChoices):
    """
    A simple class to define text choices for the 'Form' model's 'type' field.

    These choices represent different types of forms associated with the
    'Form' model.

    Choices:
    - 'TRANSACTION': Represents a form related to transactions.
    - 'FARMER': Represents a form related to farmers.
    - 'PAYMENT': Represents a form related to payments.
    """

    TRANSACTION = "TRANSACTION", _("Transaction")
    FARMER = "FARMER", _("Farmer")
    PAYMENT = "PAYMENT", _("Payment")
    PRODUCT = "PRODUCT", _("Product")


class FormFieldType(models.TextChoices):
    """
    A class to define text choices for specifying the field types in a form.

    These choices represent the types of fields that can be used in a form.

    Choices:
    - 'TEXT': Represents a text field.
    - 'NUMBER': Represents a numeric field.
    - 'EMAIL': Represents an email field.
    - 'PHONE': Represents a phone number field.
    - 'DATE': Represents a date field.
    - 'BOOLEAN': Represents a boolean (true/false) field.
    """

    TEXT = "TEXT", _("Text")
    NUMBER = "NUMBER", _("Number")
    EMAIL = "EMAIL", _("Email")
    PHONE = "PHONE", _("Phone")
    DATE = "DATE", _("Date")
    BOOLEAN = "BOOLEAN", _("Boolean")
