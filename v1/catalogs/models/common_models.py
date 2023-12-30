"""Models of the app Catalogs."""
from django.db import models
from django.utils.translation import gettext_lazy as _

from base.db.models import AbstractBaseModel


class Currency(AbstractBaseModel):
    """Currencies used in the system.

    Attribs:
        country(obj)    : currency using country.
        name(char)      : name of currency.
        code(char)      : currency code.
    """

    name = models.CharField(max_length=1000, verbose_name=_("Currency Name"))
    code = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("Currency Code"),
    )

    class Meta:
        """Meta Info."""

        verbose_name_plural = _("Currencies")
        ordering = ["name"]

    def __str__(self):
        """Object value django admin."""
        return f"{self.name} - {self.code} - {self.id}"
