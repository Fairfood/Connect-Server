"""Constants under the entities section are stored here."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class EntityStatus(models.TextChoices):
    """Enumeration of entity status.

    Represents different status values for entities.
    """

    ACTIVE = "ACTIVE", _("Active")
    INACTIVE = "INACTIVE", _("Inactive")


class CompanyMemberType(models.TextChoices):
    """Enumeration of company member types.

    Represents different types of company members.
    """

    SUPER_ADMIN = "SUPER_ADMIN", _("Super Admin")
    ADMIN = "ADMIN", _("Admin")
    REPORTER = "REPORTER", _("Reporter")


class CompanyFieldVisibiltyType(models.TextChoices):
    """Enumeration of company field visibility types.

    Represents different types of company field visibility.
    """

    TRANSACTION = "TRANSACTION", _("Transaction")
    FARMER = "FARMER", _("Farmer")


class FarmerConsentStatus(models.TextChoices):
    """Enumeration for farmer consent status.

    Represents different status values for farmer consent.
    """

    GRANTED = "GRANTED", _("Granted")
    NOT_GRANTED = "NOT_GRANTED", _("Not Granted")
    UNKNOWN = "UNKNOWN", _("Unknown")
