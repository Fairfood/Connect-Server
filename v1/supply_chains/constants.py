"""Constants under the entities section are stored here."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class EntityStatus(models.TextChoices):
    ACTIVE = "ACTIVE", _("Active")
    INACTIVE = "INACTIVE", _("Inactive")


class CompanyMemberType(models.TextChoices):
    SUPER_ADMIN = "SUPER_ADMIN", _("Super Admin")
    ADMIN = "ADMIN", _("Admin")
    REPORTER = "REPORTER", _("Reporter")


class CompanyFieldVisibiltyType(models.TextChoices):
    TRANSACTION = "TRANSACTION", _("Transaction")
    FARMER = "FARMER", _("Farmer")


class FarmerConsentStatus(models.TextChoices):
    GRANTED = "GRANTED", _("Granted")
    NOT_GRANTED = "NOT_GRANTED", _("Not Granted")
    UNKNOWN = "UNKNOWN", _("Unknown")
