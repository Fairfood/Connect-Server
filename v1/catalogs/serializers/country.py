"""Serializers related to country related apis."""
from base.drf.serializers import DynamicModelSerializer
from v1.catalogs.models import common_models as catalog_models


class ProvinceSerializer(DynamicModelSerializer):
    """Serializer for country data."""

    class Meta:
        """Meta Info."""

        model = catalog_models.Province
        exclude = ("creator", "updater", "created_on", "updated_on", "country")


class CountrySerializer(DynamicModelSerializer):
    """Serializer for province data."""

    class Meta:
        """Meta Info."""

        model = catalog_models.Country
        exclude = ("creator", "updater", "created_on", "updated_on")
