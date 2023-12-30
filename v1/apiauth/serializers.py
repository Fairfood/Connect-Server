"""Serializer customization for Authentication."""
from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import (
    TokenRefreshSerializer as SJWTTokenRefreshSerializer,
)
from rest_framework_simplejwt.state import token_backend
from rest_framework_simplejwt.tokens import RefreshToken

from base.authentication import utilities as auth_utils
from base.drf import fields
from base.exceptions import custom_exceptions as exceptions
from utilities import functions as util_functions
from v1.accounts import constants as acc_constants
from v1.accounts.models import CustomUser
from v1.accounts.models import PrivacyPolicy
from v1.accounts.models import UserDevice
from v1.accounts.models import ValidationToken
from v1.supply_chains.models.company_models import Company
from v1.supply_chains.models.company_models import CompanyMember


class APILoginSerializer(TokenObtainPairSerializer):
    """Serializer to validate and return token after logging in the user."""

    entity: Company = None
    entity_member: CompanyMember = None
    exp: int = 0
    device_id: str = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["device_id"] = serializers.CharField(required=True)
        self.fields["device_name"] = serializers.CharField(required=False)
        self.fields["device_loc"] = serializers.CharField(required=False)
        self.fields["force_logout"] = serializers.BooleanField(required=False)

    def validate(self, attrs):
        """Along with the inherited auth token and refresh token, id of user,
        and entity are added into the response."""
        self.device_id = attrs.get("device_id", None)
        force_logout = attrs.get("force_logout", False)
        device_name = attrs.get("device_name", "")
        device_loc = attrs.get("device_loc", "")

        if not self.device_id:
            raise exceptions.AuthenticationFailed(
                _("Device ID is required"), "device_id_required"
            )

        data = super().validate(attrs)
        data["user_id"] = self.user.id
        data["entity_id"] = self.entity.id

        expires_in = self.exp - timezone.now().timestamp()
        data["expires_in"] = int(expires_in if expires_in > 0 else 0)
        data["is_granted"] = True

        self.check_multiple_login(data, force_logout)
        self._get_or_create_device(device_name, device_loc)

        return data

    def get_token(self, user):
        """Get token for the user."""
        self.entity = user.get_default_entity()
        if not self.entity:
            raise exceptions.AuthenticationFailed(
                _("User does not have access any Entities")
            )
        try:
            entity_member = CompanyMember.objects.get(
                company=self.entity, user=user, is_active=True
            )
        except CompanyMember.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                _("Invalid Entity or User does not have access."),
                "invalid_entity",
            )
        token = super().get_token(user)
        self.exp = token.access_token.get("exp")
        user.set_active()
        user.disable_force_logout()
        token["session_data"] = {
            "user_id": user.id.hashid,
            "entity_id": self.entity.id.hashid,
            "member_type": entity_member.type,
            "device": self.device_id,
        }
        return token

    def _get_or_create_device(self, device_name, device_loc):
        """Get or create device for user."""
        device, created = self.user.devices.get_or_create(
            registration_id=self.device_id, user=self.user
        )
        if not created:
            device.active = True
        device.device_name = device_name
        device.device_loc = device_loc
        device.save()
        return device

    def check_multiple_login(self, data, force_logout):
        """Check if user is already logged in on another device."""
        if not self.entity.company.allow_multiple_login:
            if force_logout:
                UserDevice.deactivate_devices(self.user)

            active_devices = UserDevice.active_devices(self.user).exclude(
                registration_id=self.device_id
            )
            if active_devices.exists():
                data["is_granted"] = False
                data["access"] = ""
                data["refresh"] = ""


class TokenRefreshSerializer(SJWTTokenRefreshSerializer):
    """API to refresh token along with entity change."""

    entity = fields.SerializableRelatedField(queryset=Company.objects.all())

    def validate(self, attrs):
        """Validate the serializer data."""
        super(TokenRefreshSerializer, self).validate(attrs)
        entity = attrs["entity"]
        token_payload = token_backend.decode(attrs["refresh"])
        session_data = token_payload["session_data"]
        try:
            user = get_user_model().objects.get(
                pk=session_data["user_id"],
                status=acc_constants.UserStatus.ACTIVE,
                force_logout=False,
            )
        except get_user_model().DoesNotExist:
            raise exceptions.AuthenticationFailed(
                _("No active account found with the given credentials"),
                "no_active_account",
            )

        try:
            entity_member = CompanyMember.objects.get(
                company=entity, user=user, is_active=True
            )
        except CompanyMember.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                _("Invalid Entity or User does not have access."),
                "invalid_entity",
            )
        refresh = RefreshToken(attrs["refresh"])
        refresh["session_data"]["entity_id"] = entity.id.hashid
        attrs["refresh"] = str(refresh)
        data = super().validate(attrs)
        user.set_default_entity(entity)
        data["user_id"] = user.id.hashid
        data["entity_id"] = entity.id.hashid
        # setting expiry
        expires_in = (
            refresh.access_token.get("exp") - timezone.now().timestamp()
        )
        data["expires_in"] = int(expires_in if expires_in > 0 else 0)

        data["member_type"] = entity_member.type
        data["policy_accepted"] = user.policy_accepted
        policy = PrivacyPolicy.current_privacy_policy()
        data["current_policy"] = policy.id.hashid if policy else None
        return data


class APIPasswordResetSerializer(serializers.Serializer):
    """Serializer to send email for user password reset."""

    email = serializers.EmailField()

    def create(self, validated_data):
        """Create overrided to return the validated data."""
        try:
            ip, location, device = util_functions.client_details(
                (self.context["request"])
            )
            user = CustomUser.objects.get(
                email=validated_data["email"], is_active=True
            )
            user.reset_password(ip, location, device)
        except CustomUser.DoesNotExist:
            raise exceptions.BadRequest(
                _("Email is not registered with any user")
            )
        return validated_data

    def to_representation(self, instance):
        """Represent the serializer data."""
        return {}


class ValidationSerializer(serializers.Serializer):
    """Serializer to send email for user password reset."""

    validation_token = serializers.CharField(required=False)
    user = fields.SerializableRelatedField(
        queryset=CustomUser.objects.all(), required=False
    )
    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=False)
    entity = fields.SerializableRelatedField(
        queryset=Company.objects.all(), required=False, allow_null=True
    )

    def validate_validation_token(self, value):
        """Validate the validation token."""
        token_validation = {
            "valid": True,
            "value": value,
            "message": "",
            "set_password": False,
        }
        try:
            validation_token = ValidationToken.objects.get(key=value)

            token_validation["object"] = validation_token
            if not validation_token.is_valid():
                token_validation["valid"] = False
                token_validation["message"] = _("Invalid validation token")
                # raise serializers.ValidationError(
                #     _("Invalid validation token"))
        except ValidationToken.DoesNotExist:
            token_validation["valid"] = False
            token_validation["message"] = _("Invalid validation token")
            # raise serializers.ValidationError(_("Invalid validation token"))
        return token_validation

    def validate_email(self, value):
        """Validate the email."""
        email_validation = {
            "valid": True,
            "value": value,
            "message": "",
        }
        if CustomUser.objects.filter(email=value).exists():
            email_validation["valid"] = False
            email_validation["message"] = _("Email already taken.")
        return email_validation

    def validate_password(self, value):
        """Validate the password."""
        password_validate = {
            "valid": True,
            "value": value,
            "message": "",
        }
        try:
            password_validation.validate_password(value)
        except Exception as e:
            password_validate["valid"] = False
            password_validate["message"] = str(e)
        return password_validate

    def validate(self, attrs):
        """Validate the serializer data."""
        user = attrs.get("user", None)
        attrs["user"] = user.id.id
        entity = attrs.pop("entity", None)
        validation_token = attrs.get("validation_token", {"object": None}).pop(
            "object"
        )
        if entity and not entity.entity_members.filter(user=user).exists():
            raise serializers.ValidationError(
                _("Member is removed or not available, please contact admin.")
            )
        if validation_token:
            if not user:
                raise serializers.ValidationError(
                    {
                        "validation_token": [
                            _(
                                "User ID is required to validate "
                                "Validation Token"
                            )
                        ]
                    }
                )
            if (
                not user.password
                or not user.has_usable_password()
                or validation_token.type
                == acc_constants.ValidationTokenType.RESET_PASS
            ):
                attrs["validation_token"]["set_password"] = True
            if user != getattr(validation_token, "user", None):
                attrs["validation_token"]["value"] = "-"
                attrs["validation_token"]["valid"] = False
                attrs["validation_token"]["message"] = _(
                    "Invalid validation token"
                )
        return attrs

    def create(self, validated_data):
        """Create overrided to return the validated data."""
        return validated_data

    def to_representation(self, instance):
        """Represent the serializer data."""
        return instance


class PasswordResetConfirmSerializer(ValidationSerializer):
    """Serializer to change password of user."""

    token = serializers.CharField()
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)
    old_password = serializers.CharField(max_length=128, required=False)

    def validate(self, attrs):
        """Validate the serializer data."""
        attrs = super(PasswordResetConfirmSerializer, self).validate(attrs)
        try:
            attrs["token"] = ValidationToken.objects.get(
                key=attrs.get("token")
            )
        except ValidationToken.DoesNotExist:
            raise exceptions.BadRequest(_("Token does not exist."))
        try:
            attrs["user"] = CustomUser.objects.get(id=attrs.get("user"))
        except CustomUser.DoesNotExist:
            raise exceptions.BadRequest(_("User does not exist"))
        if (
            attrs["user"].password
            and attrs["user"].has_usable_password()
            and attrs["token"].type
            != acc_constants.ValidationTokenType.RESET_PASS
        ):
            raise serializers.ValidationError(
                _(
                    "Password already set. "
                    "User reset password to change password."
                )
            )
        if attrs.get("old_password", None) and not attrs[
            "user"
        ].check_password(attrs["old_password"]):
            raise serializers.ValidationError(_("Password is incorrect."))
        if attrs["new_password1"] != attrs["new_password2"]:
            raise serializers.ValidationError(
                _("Your passwords didn't match.")
            )
        return attrs

    def create(self, validated_data):
        """Create and return a new `User` instance, given the validated
        data."""
        super(PasswordResetConfirmSerializer, self).create(validated_data)
        user = validated_data["user"]
        user.set_password(validated_data["new_password1"])
        if (
            validated_data["token"].type
            == acc_constants.ValidationTokenType.INVITE
        ):
            user.accepted_policy = PrivacyPolicy.current_privacy_policy()
        user.save()
        validated_data["token"].invalidate()
        return validated_data

    def to_representation(self, instance):
        """Represent the serializer data."""
        return {}


class CheckPasswordSerializer(serializers.Serializer):
    """Serializer to check user password is correct."""

    password = serializers.CharField()

    def create(self, validated_data):
        """Create overrided to check the password is correct."""
        user = auth_utils.get_current_user()
        if not user.check_password(validated_data["password"]):
            raise exceptions.NoValueResponse(_("Password is incorrect"))
        return validated_data

    def to_representation(self, instance):
        """Return success response."""
        return {"message": "Password is correct"}
