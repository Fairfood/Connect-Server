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
        verbose_name=_("Creator"),
    )
    updater = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        default=None,
        null=True,
        blank=True,
        related_name="updater_%(class)s_objects",
        on_delete=models.SET_NULL,
        verbose_name=_("Updater"),
    )
    updated_on = models.DateTimeField(
        auto_now=True, verbose_name=_("Updated On")
    )
    created_on = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Updated On")
    )

    class Meta:
        """Meta class for the above model."""

        abstract = True
        ordering = ("-created_on",)

    def save(self, *args, **kwargs):
        """Override save method to add creator and updater."""
        current_user = auth_utils.get_current_user()
        if current_user:
            if not self.pk and not self.creator:
                self.creator = current_user
            self.updater = current_user
        self.new_instance = not self.pk
        super(AbstractBaseModel, self).save(*args, **kwargs)

    @classmethod
    def field_names(cls) -> list:
        """Return list of field names."""
        return [field.name for field in cls._meta.get_fields()]

    @classmethod
    def clean_dict(cls, data: dict, extra_keys: set = None) -> dict:
        """Clean dict to remove extra keys.

        Args:
            data(dict): Data to be cleaned
            extra_keys(set): Extra keys to be removed
        """
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
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    zipcode = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        """Meta class defines class level configurations."""

        abstract = True


class AbstractNumberedModel(models.Model):
    """Abstract base class to use to automatically add a number field to track
    a number tracked that can be shown in the frontend."""

    number = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Override save method to add number."""
        super(AbstractNumberedModel, self).save(*args, **kwargs)
        if not self.number:
            self.number = str(self.id.id + 1000)
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
