"""Constants under the catalogs section are stored here."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class CategoryType(models.IntegerChoices):
    """A class to define integer choices for the 'Category' model's 'type'
    field.

    Choices:
    - ENTITY_DOCUMENT: Represents an entity document with a value of 101.
    """

    ENTITY_DOCUMENT = 101, _("Entity Document")
