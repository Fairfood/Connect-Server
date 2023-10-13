"""Serializers related to currency related apis."""
from rest_framework import serializers

from base.drf import fields
from v1.catalogs import models as catalog_models


class CurrencySerializer(serializers.ModelSerializer):
    """Serializer for currency data."""

    id = fields.SerializableRelatedField(read_only=True)

    class Meta:
        """Meta Info."""

        model = catalog_models.Currency
        fields = ("id", "name", "code")
