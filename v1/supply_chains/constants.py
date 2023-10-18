"""Constants under the entities section are stored here."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class EntityStatus(models.TextChoices):
    ACTIVE = "ACT", _("Active")
    INACTIVE = "INA", _("Inactive")


class CompanyMemberType(models.TextChoices):
    SUPER_ADMIN = "SUP", _("Super Admin")
    ADMIN = "ADM", _("Admin")
    REPORTER = "REP", _("Reporter")


class CompanyFieldType(models.TextChoices):
    TEXT = "TXT", _("Text")
    NUMBER = "NUM", _("Number")
    BOOL = "BOL", _("Boolean")


class CompanyFieldVisibiltyType(models.TextChoices):
    TRANSACTION = "TRA", _("Transaction")
    FARMER = "FAR", _("Farmer")


class FarmerConsentStatus(models.TextChoices):
    GRANTED = "GRA", _("Granted")
    NOT_GRANTED = "NOT", _("Not Granted")
    UNKNOWN = "UNK", _("Unknown")
