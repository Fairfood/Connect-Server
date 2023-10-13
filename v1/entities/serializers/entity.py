from django.db import transaction as django_transaction
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from base.authentication import utilities as auth_utils
from base.drf import fields
from v1.accounts import models as user_models
from v1.catalogs import models as catalog_models
from v1.catalogs.serializers import category as category_serializer
from v1.catalogs.serializers import country as country_serializer
from v1.entities import constants as entity_consts
from v1.entities import models as entity_models


class BasicEntitySerializer(serializers.ModelSerializer):
    """"""

    id = fields.SerializableRelatedField(read_only=True)
    bc_address = serializers.SerializerMethodField()

    def get_bc_address(self, obj):
        """"""
        return "Block chain is not linked."

    class Meta:
        """Meta data."""

        model = entity_models.Entity
        fields = ("id", "name", "image", "phone", "bc_address", "operation")


class EntitySerializer(serializers.ModelSerializer):
    """"""

    id = fields.SerializableRelatedField(read_only=True)
    phone = PhoneNumberField(required=False, allow_blank=True, allow_null=True)
    date_invited = serializers.DateTimeField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    members = fields.SerializableRelatedField(
        queryset=user_models.CustomUser.objects.all(),
        required=False,
        many=True,
    )
    country = fields.SerializableRelatedField(
        serializer=country_serializer.BaseCountrySerializer,
        queryset=catalog_models.Country.objects.all(),
    )
    province = fields.SerializableRelatedField(
        serializer=country_serializer.ProvinceSerializer,
        queryset=catalog_models.Province.objects.all(),
        required=False,
    )
    incharge = fields.SerializableRelatedField(
        required=False,
        queryset=user_models.CustomUser.objects.all(),
        allow_null=True,
    )
    invited_by = fields.SerializableRelatedField(
        queryset=entity_models.Entity.objects.all()
    )
    profile_completion = serializers.FloatField(read_only=True)
    can_edit = serializers.BooleanField(
        read_only=True, source="can_be_edited_by"
    )

    class Meta:
        """Meta data."""

        model = entity_models.Entity
        exclude = (
            "updater",
            "creator",
            "updated_on",
            "created_on",
        )

    def create(self, validated_data):
        validated_data["invited_by"] = validated_data.get(
            "invited_by", auth_utils.get_current_entity()
        )
        return super(EntitySerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        instance = super(EntitySerializer, self).update(
            instance, validated_data
        )
        if instance.members.count() == 1:
            member = instance.members.first()
            if not member.password:
                from v1.accounts.serializers.user import UserSerializer

                UserSerializer.create_update_user(
                    instance=instance.members.first(),
                    validated_data=validated_data,
                )
                instance.send_invite()
        return instance

    def to_representation(self, instance):
        data = super(EntitySerializer, self).to_representation(instance)
        return data


class EntityDocumentSerializer(serializers.ModelSerializer):
    """"""

    id = fields.SerializableRelatedField(read_only=True)
    category = fields.SerializableRelatedField(
        serializer=category_serializer.CategorySerializer,
        queryset=catalog_models.Category.objects.all(),
        required=False,
    )

    # extra data about logged-in user's previleges over the entity-member.
    extra_info = serializers.SerializerMethodField()

    class Meta:
        """"""

        fields = (
            "id",
            "name",
            "file",
            "entity",
            "category",
            "is_deleted",
            "extra_info",
        )
        model = entity_models.EntityDocument

    def get_extra_info(self, obj):
        """Return the logged-in user can change the data of the entity-
        member."""
        current_user = auth_utils.get_current_user()
        entity = auth_utils.get_current_entity()
        types = [
            entity_consts.EntityMemberType.ADMIN,
            entity_consts.EntityMemberType.SUPER_ADMIN,
        ]
        member = current_user.member_entitys.filter(
            type__in=types, entity=entity
        )
        data = {"can_edit": False, "can_remove": False}
        if obj.creator == current_user:
            data["can_edit"] = True
        if member.exists():
            data["can_edit"] = True
            data["can_remove"] = True
        return data

    def create(self, validated_data):
        """"""
        validated_data["entity"] = auth_utils.get_current_entity()
        document = super(EntityDocumentSerializer, self).create(validated_data)
        document.notify()
        return document


class EntityMemberSerializer(serializers.ModelSerializer):
    """"""

    id = fields.SerializableRelatedField(read_only=True)
    user_id = fields.SerializableRelatedField(source="user.id", read_only=True)
    name = serializers.CharField(source="user.name")
    email = serializers.CharField(source="user.email")
    image = serializers.ImageField(source="user.image", read_only=True)
    status = serializers.IntegerField(source="user.status", read_only=True)

    # extra data about logged-in user's previleges over the entity-member.
    extra_info = serializers.SerializerMethodField()

    class Meta:
        """"""

        model = entity_models.EntityMember
        fields = (
            "id",
            "user_id",
            "name",
            "type",
            "image",
            "email",
            "status",
            "extra_info",
        )

    def get_extra_info(self, obj):
        """Return the logged-in user can change the data of the entity-
        member."""
        current_user = auth_utils.get_current_user()

        current_user_is_admin = obj.entity.entity_members.filter(
            user=current_user, type=entity_consts.EntityMemberType.SUPER_ADMIN
        ).exists()

        data = {"can_edit": False, "can_remove": False}
        if obj.user != current_user and current_user_is_admin:
            data["can_edit"] = True
            data["can_remove"] = True
        return data

    @staticmethod
    def create_user(validated_data):
        """Creates user account for Entity incharge."""
        from v1.accounts.serializers.user import UserSerializer

        return UserSerializer.create_update_user(validated_data=validated_data)

    def create(self, validated_data):
        """Craete overrided."""
        validated_data["entity"] = auth_utils.get_current_entity()
        validated_data.update(**validated_data["user"])
        user = self.create_user(validated_data)
        validated_data["user"] = user
        member_data = entity_models.EntityMember.clean_dict(validated_data)

        member = super().create(member_data)
        member.send_invite()
        return member

    @django_transaction.atomic
    def update(self, instance, validated_data):
        """Update overrided to change updater and notify the user."""
        if (
            "type" in validated_data.keys()
            and validated_data["type"] != instance.type
        ):
            instance.user.make_force_logout()
        member = super().update(instance, validated_data)
        return member
