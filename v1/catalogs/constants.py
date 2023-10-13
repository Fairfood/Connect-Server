"""Constants under the catalogs section are stored here."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class CategoryType(models.IntegerChoices):

    ENTITY_DOCUMENT = 101, _('Entity Document')
    