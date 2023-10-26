"""Models of the app Catalogs."""
from django.db import models
from django.utils.translation import gettext_lazy as _

from base.db.models import AbstractBaseModel
from v1.accounts import constants as user_consts


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


class Country(AbstractBaseModel):
    """Model to save countries.

    Attribs:
        name(char)      : name of the country.
        latitude(char)  : latitude of the country.
        longitude(char) : longitude of the country.
        code(char)      : country code.
        dial_code(char) : country dial code.
    """

    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name="countries",
        verbose_name=_("Currency"),
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=1000, verbose_name=_("Country Name"))
    latitude = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name=_("Latitude"),
    )
    longitude = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name=_("Longitude"),
    )
    alpha_2 = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name=_("Country Code"),
    )
    alpha_3 = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name=_("CCA3 Country Code"),
    )
    dial_code = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("Dial Code"),
    )
    language = models.CharField(
        max_length=10,
        verbose_name=_("Selected Language"),
        default=user_consts.Language.ENGLISH,
        choices=user_consts.Language.choices,
    )

    class Meta:
        verbose_name_plural = _("Countries")
        ordering = ["name"]

    def __str__(self):
        """Function to return value in django admin."""
        return f"{self.alpha_2} - {self.name}"


class Province(AbstractBaseModel):
    """Provinces of each countries are stored here.

    Attribs:
        country(obj)    : country of the province.
        name(char)      : name of the province.
        latitude(char)  : latitude of the province.
        longitude(char) : longitude of the province.
    """

    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="provinces",
        verbose_name=_("Country"),
    )
    name = models.CharField(max_length=1000, verbose_name=_("Province Name"))
    latitude = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name=_("Latitude"),
    )
    longitude = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name=_("Longitude"),
    )

    class Meta:
        """"""

        ordering = ["country__name"]

    def __str__(self):
        """Function to return value in django admin."""
        return (
            f"{self.country.name} - "
            f"{self.name}  - "
            f"{self.latitude} - "
            f"{self.longitude}"
        )
