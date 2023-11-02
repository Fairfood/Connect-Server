from rest_framework import serializers

from base.drf.serializers import DynamicModelSerializer
from v1.catalogs.serializers.products import ConnectCardSerializer
from v1.forms.serializers import FormSerializer
from v1.forms.serializers import ReferenceFormSerializer
from v1.supply_chains.models.base_models import Entity
from v1.supply_chains.models.base_models import EntityCard
from v1.supply_chains.models.company_models import Company
from v1.supply_chains.models.company_models import CompanyFieldVisibilty
from v1.supply_chains.models.farmer_models import Farmer


class EntityCardSerializer(DynamicModelSerializer):
    """
    Serializer for the EntityCard model.
    """

    card = ConnectCardSerializer()

    class Meta:
        model = EntityCard
        fields = "__all__"


class EntitySerializer(DynamicModelSerializer):
    """
    Serializer for the Entity model.
    """

    name = serializers.CharField(source="entity_name", read_only=True)

    class Meta:
        model = Entity
        fields = "__all__"


class CompanyFieldVisibiltySerilizer(DynamicModelSerializer):
    class Meta:
        model = CompanyFieldVisibilty
        fields = "__all__"


class CompanySerializer(DynamicModelSerializer):
    """
    Serializer for the Company model.
    """

    buyer = EntitySerializer(
        read_only=True, fields=("id", "name", "image", "description")
    )
    entity_card = EntityCardSerializer(read_only=True)
    reference_forms = ReferenceFormSerializer(many=True, read_only=True)
    field_visibilties = CompanyFieldVisibiltySerilizer(
        many=True, read_only=True
    )

    class Meta:
        model = Company
        fields = "__all__"


class FarmerSerializer(DynamicModelSerializer):
    """
    Serializer for the Farmer model.
    """

    entity_card = EntityCardSerializer(read_only=True)
    forms = FormSerializer(many=True)

    class Meta:
        model = Farmer
        fields = "__all__"
