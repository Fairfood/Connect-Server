"""Serializers related to country related apis."""

from rest_framework import serializers

from base.drf import fields

from v1.catalogs import models as catalog_models
from v1.catalogs.serializers.currency import CurrencySerializer


class VillageSerializer(serializers.ModelSerializer):
    """
    Serializer for Region data.
    """
    id = fields.SerializableRelatedField(read_only=True)
    region = fields.SerializableRelatedField(
        write_only=True, queryset=catalog_models.Region.objects.all())

    class Meta:
        """
        Meta Info.
        """
        model = catalog_models.Village
        exclude = ('creator', 'updater', 'created_on', 'updated_on', )


class RegionSerializer(serializers.ModelSerializer):
    """
    Serializer for Region data.
    """
    id = fields.SerializableRelatedField(read_only=True)
    villages = fields.SerializableRelatedField(
        serializer=VillageSerializer, read_only=True, many=True)

    class Meta:
        """
        Meta Info.
        """
        model = catalog_models.Region
        exclude = ('creator', 'updater', 'created_on', 'updated_on', 'province')


class ProvinceSerializer(serializers.ModelSerializer):
    """
    Serializer for country data.
    """

    id = fields.SerializableRelatedField(read_only=True)
    regions = fields.SerializableRelatedField(
        serializer=RegionSerializer, read_only=True, many=True )

    class Meta:
        """
        Meta Info.
        """
        model = catalog_models.Province
        exclude = ('creator', 'updater', 'created_on', 'updated_on', 'country')


class CountrySerializer(serializers.ModelSerializer):
    """
    Serializer for province data.
    """

    id = fields.SerializableRelatedField(read_only=True)
    provinces = fields.SerializableRelatedField(
        serializer=ProvinceSerializer, read_only=True, many=True)
    currency = fields.SerializableRelatedField(read_only=True)

    class Meta:
        """
        Meta Info.
        """
        model = catalog_models.Country
        exclude = ('creator', 'updater', 'created_on', 'updated_on')


class BaseCountrySerializer(serializers.ModelSerializer):
    """
    Serializer for province data.
    """

    id = fields.SerializableRelatedField(read_only=True)
    class Meta:
        """
        Meta Info.
        """
        model = catalog_models.Country
        exclude = ('creator', 'updater', 'created_on', 'updated_on')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data


class BaseRegionSerializer(serializers.ModelSerializer):
    """
    Serializer for Region data.
    """
    id = fields.SerializableRelatedField(read_only=True)

    class Meta:
        """
        Meta Info.
        """
        model = catalog_models.Region
        fields = ('id', 'name')


class BaseProvinceSerializer(serializers.ModelSerializer):
    """
    Serializer for country data.
    """

    id = fields.SerializableRelatedField(read_only=True)

    class Meta:
        """
        Meta Info.
        """
        model = catalog_models.Province
        fields = ('id', 'name')
