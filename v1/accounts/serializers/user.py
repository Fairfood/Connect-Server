"""Serializers related to user are stored here."""
from rest_framework import serializers

from base.drf import fields
from base.drf.serializers import DynamicModelSerializer
from v1.accounts import models as user_models
from v1.accounts.serializers.other_apps import UserEntitySerializer


class UserSerializer(DynamicModelSerializer):
    """Serializer for user."""

    managing_entitys = fields.SerializableRelatedField(
        read_only=True,
        serializer=UserEntitySerializer,
        source="member_companies",
        many=True,
    )

    default_entity = fields.SerializableRelatedField(read_only=True)
    phone = fields.PhoneNumberField(
        required=False, allow_blank=True, allow_null=True
    )
    accepted_policy = fields.SerializableRelatedField(
        required=False, queryset=user_models.PrivacyPolicy.objects.all()
    )
    current_policy = serializers.SerializerMethodField()
    language = serializers.CharField(required=False)

    class Meta:
        """Meta info."""

        model = user_models.CustomUser
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "dob",
            "phone",
            "address",
            "image",
            "updated_email",
            "managing_entitys",
            "default_entity",
            "accepted_policy",
            "policy_accepted",
            "current_policy",
            "language",
        ]

    def get_current_policy(self, obj):
        """Return current policy."""
        policy = user_models.PrivacyPolicy.current_privacy_policy()
        return policy.id if policy else None

    @staticmethod
    def create_update_user(validated_data, instance=None):
        """Creates user account for Entity incharge."""
        if not instance:
            if validated_data.get("email", None):
                matching_users = user_models.CustomUser.objects.filter(
                    email=validated_data["email"]
                )
                if matching_users.exists():
                    return matching_users.first()
            elif validated_data.get("phone", None):
                matching_users = user_models.CustomUser.objects.filter(
                    phone=validated_data["phone"]
                )
                if matching_users.exists():
                    return matching_users.first()
            else:
                return None
        validated_data["contact_name"] = validated_data.get(
            "contact_name", None
        ) or validated_data.get("name", " ")
        user_data = user_models.CustomUser.clean_dict(validated_data)
        name = validated_data["contact_name"].strip().split(" ")
        user_data["first_name"], user_data["last_name"] = name[0], " ".join(
            name[1:]
        )
        user_serializer = UserSerializer(
            instance=instance, data=user_data, partial=True
        )
        if not user_serializer.is_valid():
            raise serializers.ValidationError(user_serializer.errors)
        return user_serializer.save()


class BasicUserSerializer(serializers.ModelSerializer):
    """Serializer for basic user information.

    This serializer is used to represent basic information about a user.
    """

    id = fields.SerializableRelatedField(read_only=True)

    class Meta:
        """Meta info."""

        model = user_models.CustomUser
        fields = ["id", "first_name", "last_name", "email", "image"]


class PrivacyPolicySerializer(serializers.ModelSerializer):
    """Serializer for Privacy policy."""

    id = fields.SerializableRelatedField(read_only=True)

    class Meta:
        """Meta info."""

        model = user_models.PrivacyPolicy
        fields = ["id", "content", "version", "date", "since"]
