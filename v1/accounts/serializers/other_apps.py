"""Serializer used in accounts app not from accounts apps are stored here."""
from rest_framework import serializers

from base.drf import fields
from v1.supply_chains.models import company_models


class UserEntitySerializer(serializers.ModelSerializer):
    """Serializer for entity data in user details."""

    id = fields.SerializableRelatedField(source="entity.id", read_only=True)
    name = serializers.CharField(source="entity.name")
    image = serializers.FileField(source="entity.image")
    member_role = serializers.CharField(source="type")
    email = serializers.EmailField(source="entity.email")

    class Meta:
        """Meta Info."""

        model = company_models.CompanyMember
        fields = ("id", "company", "member_role", "image", "email")
