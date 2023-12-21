"""Serializer used in accounts app not from accounts apps are stored here."""
from rest_framework import serializers

from base.drf import fields
from v1.supply_chains.models import company_models


class UserEntitySerializer(serializers.ModelSerializer):
    """Serializer for entity data in user details."""

    id = fields.SerializableRelatedField(source="company.id", read_only=True)
    name = serializers.CharField(source="company.name")
    image = serializers.FileField(source="company.image")
    member_role = serializers.CharField(source="type")
    email = serializers.EmailField(source="company.email")

    class Meta:
        """Meta Info."""

        model = company_models.CompanyMember
        fields = ("id", "name", "member_role", "image", "email")
