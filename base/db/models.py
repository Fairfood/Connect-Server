"""Models commonly used in all apps."""
import copy

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from hashid_field import HashidAutoField

from base.authentication import utilities as auth_utils


class AbstractBaseModel(models.Model):
    """Abstract base model for tracking.

    Atribs:
        creator(obj): Creator of the object
        updater(obj): Updater of the object
        created_on(datetime): Added date of the object
        updated_on(datetime): Last updated date of the object
    """

    id = HashidAutoField(primary_key=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        default=None,
        null=True,
        blank=True,
        related_name="creator_%(class)s_objects",
        on_delete=models.SET_NULL,
    )
    updater = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        default=None,
        null=True,
        blank=True,
        related_name="updater_%(class)s_objects",
        on_delete=models.SET_NULL,
    )
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta class for the above model."""

        abstract = True
        ordering = ("-created_on",)

    def save(self, *args, **kwargs):
        current_user = auth_utils.get_current_user()
        if current_user:
            if not self.pk:
                self.creator = current_user
            self.updater = current_user
        self.new_instance = not self.pk
        super(AbstractBaseModel, self).save(*args, **kwargs)

    @classmethod
    def field_names(cls) -> list:
        return [field.name for field in cls._meta.get_fields()]

    @classmethod
    def clean_dict(cls, data: dict, extra_keys: set = None) -> dict:
        # Patch for multipart request with file
        # 1. AttributeError: 'NoneType' object has no attribute 'seek'
        #    Occurs on deepcopy
        # 2. Reinserting image to validated_data

        image = data.pop("image", None)
        extra_keys = extra_keys or set()
        n_data = copy.deepcopy(data)
        keys_needed = set(cls.field_names()) | extra_keys
        keys_to_remove = list(keys_needed ^ {*n_data})
        [n_data.pop(key, None) for key in keys_to_remove]
        if image:
            data["image"] = image
            if "image" in keys_needed:
                n_data["image"] = image
        return n_data


class AbstractAddressModel(models.Model):
    """Abstract model to group fields related to address."""

    house_name = models.CharField(max_length=100, null=True, blank=True)
    street = models.CharField(max_length=500, null=True, blank=True)
    city = models.CharField(max_length=500, null=True, blank=True)
    sub_province = models.CharField(max_length=500, null=True, blank=True)
    province = models.CharField(max_length=500, null=True, blank=True)
    country = models.CharField(max_length=500, null=True, blank=True)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    zipcode = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        """Meta class defines class level configurations."""

        abstract = True


class AbstractNumberedModel(models.Model):
    """Abstract base class to use to automatically add a number field to track
    a number tracked that can be shown in the frontend."""

    number = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super(AbstractNumberedModel, self).save(*args, **kwargs)
        if not self.number:
            self.number = self.id.id + 1000
            self.save()


class AbstractContactModel(models.Model):
    """Abstract model to group fields related to contact."""

    email = models.EmailField(
        max_length=100, blank=True, null=True, verbose_name=_("Email Address")
    )
    phone = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("Phone Number"),
    )

    class Meta:
        """Meta class defines class level configurations."""

        abstract = True


class AbstarctAditionalField(AbstractBaseModel):
    """
    An abstract model for additional fields associated an entity
    (Farmer, Transaction etc.).

    Attributes:
    - field (CompanyAdditionalField): The specific additional field.
    - value (str): The value associated with the additional field.

    Note:
    This is an abstract model that defines the structure for handling
    additional fields associated with payments. It should be used as a base for
    concrete models that capture payment-specific additional fields.
    """

    field = models.ForeignKey(
        "supply_chains.CompanyAdditionalField",
        on_delete=models.CASCADE,
        related_name="%(class)s_payment_values",
        verbose_name=_("Field"),
    )
    value = models.CharField(max_length=100, verbose_name=_("Value"))

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.field.name} -> {self.value}"
