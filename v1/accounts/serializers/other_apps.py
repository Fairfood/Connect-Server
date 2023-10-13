"""Serializer used in accounts app not from accounts apps are stored here."""

from rest_framework import serializers

from base.drf import fields

from v1.entities import models as entity_models


class UserEntitySerializer(serializers.ModelSerializer):
    """
    Serializer for entity data in user details
    """
    id = fields.SerializableRelatedField(source='entity.id', read_only=True)
    name = serializers.CharField(source='entity.name')
    image = serializers.FileField(source='entity.image')
    entity_type = serializers.IntegerField(source='entity.type')
    member_role = serializers.IntegerField(source='type')
    email = serializers.EmailField(source='entity.email')

    class Meta:
        """Meta Info."""
        model = entity_models.EntityMember
        fields = ('id', 'name', 'entity_type', 'member_role', 'image', 'email')
