"""serializers related to category."""

from rest_framework import serializers

from base.authentication import utilities as auth_utils
from base.authentication import session

from base.drf import fields

from v1.catalogs import models as catalog_models


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for category."""

    id = fields.SerializableRelatedField(read_only=True)
    
    class Meta:
        """Meta Info."""
        model = catalog_models.Category
        exclude = ('created_on', 'updated_on', 'creator', 'updater')

    def create(self, validated_data):
        """Create overrided to add creator."""
        return super().create(validated_data)
