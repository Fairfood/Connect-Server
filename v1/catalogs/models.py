"""Models of the app Catalogs."""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from base.db.models import AbstractBaseModel
from utilities.url_utils import URL

from v1.blockchain.models.create_topic import AbstractTopic

from v1.catalogs import constants as catalog_consts
from v1.accounts import constants as user_consts


class Currency(AbstractBaseModel):
    """
    Currencies used in the system.
    Attribs:
        country(obj)    : currency using country.
        name(char)      : name of currency.
        code(char)      : currency code.
    """

    name = models.CharField(
        max_length=1000, verbose_name=_('Currency Name'))
    code = models.CharField(
        max_length=100, default='', null=True, blank=True,
        verbose_name=_('Currency Code'))

    class Meta:
        """Meta Info."""
        verbose_name_plural = _('Currencies')
        ordering = ['name']

    def __str__(self):
        """
        Object value django admin.
        """
        return f'{self.name} - {self.code} - {self.id}'


class Country(AbstractBaseModel):
    """
    Model to save countries.

    Attribs:
        name(char)      : name of the country.
        latitude(char)  : latitude of the country.
        longitude(char) : longitude of the country.
        code(char)      : country code.
        dial_code(char) : country dial code.
    """

    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE,
        related_name='countries', verbose_name=_('Currency'),
        null=True, blank=True)
    name = models.CharField(
        max_length=1000, verbose_name=_('Country Name'))
    latitude = models.CharField(
        max_length=500, default='', null=True, blank=True, 
        verbose_name=_('Latitude'))
    longitude = models.CharField(
        max_length=500, default='', null=True, blank=True, 
        verbose_name=_('Longitude'))
    alpha_2 = models.CharField(
        max_length=10, default='', null=True, blank=True,
        verbose_name=_('Country Code'))
    alpha_3 = models.CharField(
        max_length=10, default='', null=True, blank=True,
        verbose_name=_('CCA3 Country Code'))
    dial_code = models.CharField(
        max_length=100, default='', null=True, blank=True, 
        verbose_name=_('Dial Code'))
    language = models.CharField(
        max_length=10, verbose_name=_('Selected Language'),
        default=user_consts.Language.ENGLISH,
        choices=user_consts.Language.choices)
    
    class Meta:
        verbose_name_plural = _('Countries')
        ordering = ['name']
    
    def __str__(self):
        """Function to return value in django admin."""
        return f'{self.alpha_2} - {self.name}'


class Province(AbstractBaseModel):
    """
    Provinces of each countries are stored here.

    Attribs:
        country(obj)    : country of the province.
        name(char)      : name of the province.
        latitude(char)  : latitude of the province.
        longitude(char) : longitude of the province.
    """
    
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, 
        related_name='provinces', verbose_name=_('Country'))
    name = models.CharField(
        max_length=1000, verbose_name=_('Province Name'))
    latitude = models.CharField(
        max_length=500, default='', null=True, blank=True, 
        verbose_name=_('Latitude'))
    longitude = models.CharField(
        max_length=500, default='', null=True, blank=True, 
        verbose_name=_('Longitude'))

    class Meta:
        """"""
        ordering = ['country__name']
    
    def __str__(self):
        """Function to return value in django admin."""
        return f'{self.country.name} - {self.name}  - {self.latitude} - \
            {self.longitude}'


class Region(AbstractBaseModel):
    """
    Region of each province are stored here.

    Attribs:
        province(obj)    : province of the region.
        name(char)      : name of the region.
    """
    province = models.ForeignKey(
        Province, on_delete=models.CASCADE,
        related_name='regions', verbose_name=_('Province'))
    name = models.CharField(
        max_length=1000, verbose_name=_('Region Name'))

    def __str__(self):
        """Function to return value in django admin."""
        return f'{self.province.country.name} - {self.province.name}  - {self.name}'


class Village(AbstractBaseModel):
    """
    Region of each province are stored here.

    Attribs:
        region(obj)    : region of the village.
        name(char)      : name of the region.
    """
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE,
        related_name='villages', verbose_name=_('Region'))
    name = models.CharField(
        max_length=1000, verbose_name=_('Village Name'))

    def __str__(self):
        """Function to return value in django admin."""
        return f'{self.region.province.country.name} - {self.region.province.name} - \
               {self.name}'


class Category(AbstractBaseModel):
    """
    Model to store categories used in the system.

    Attribs:
        name(char)      : Category name.
        type(int)       : Type of the category(choice).
        is_active(bool) : Is cateogry active or not.
    """

    name = models.CharField(
        max_length=1000, default='', null=True, blank=True, 
        verbose_name=_('Category Name'))
    type = models.IntegerField(
        default=catalog_consts.CategoryType.ENTITY_DOCUMENT,
        choices=catalog_consts.CategoryType.choices, 
        verbose_name=_('Category Type'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))

    class Meta:
        """Meta Info."""
        verbose_name_plural = _('Categories')
        ordering = ['name']

    def __str__(self):
        """
        Object value django admin.
        """
        return f'{self.name} - {self.get_type_display()} - {self.id}'
