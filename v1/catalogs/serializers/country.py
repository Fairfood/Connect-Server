"""Serializers related to country related apis."""
from rest_framework import serializers

from base.drf import fields
from v1.catalogs.models import common_models as catalog_models


class ProvinceSerializer(serializers.ModelSerializer):
    """Serializer for country data."""

    id = fields.SerializableRelatedField(read_only=True)

    class Meta:
        """Meta Info."""

        model = catalog_models.Province
        exclude = ("creator", "updater", "created_on", "updated_on", "country")


class CountrySerializer(serializers.ModelSerializer):
    """Serializer for province data."""

    id = fields.SerializableRelatedField(read_only=True)
    provinces = fields.SerializableRelatedField(
        serializer=ProvinceSerializer, read_only=True, many=True
    )
    currency = fields.SerializableRelatedField(read_only=True)

    class Meta:
        """Meta Info."""

        model = catalog_models.Country
        exclude = ("creator", "updater", "created_on", "updated_on")
