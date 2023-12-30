"""Serializers related to currency related apis."""
from base.drf.serializers import DynamicModelSerializer
from v1.catalogs.models import common_models as catalog_models


class CurrencySerializer(DynamicModelSerializer):
    """Serializer for currency data."""

    class Meta:
        """Meta Info."""

        model = catalog_models.Currency
        fields = ("id", "name", "code")
