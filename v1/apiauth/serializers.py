"""Serializer customization for Authentication."""

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model, password_validation
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import \
    TokenRefreshSerializer as SJWTTokenRefreshSerializer
from rest_framework_simplejwt.state import token_backend
from rest_framework_simplejwt.tokens import RefreshToken

from base.authentication import utilities as auth_utils
from base.drf import fields
from base.drf import utils as base_utils
from base.exceptions import custom_exceptions as exceptions
from utilities import functions as util_functions
from v1.accounts import constants as acc_constants
from v1.accounts.constants import DeviceType
from v1.accounts.models import (CustomUser, PrivacyPolicy, UserDevice,
                                ValidationToken)
from v1.supply_chains.models.company_models import Company, CompanyMember

from . import models as auth_models


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
        self.fields["version"] = serializers.CharField(required=False)
        self.fields["force_logout"] = serializers.BooleanField(required=False)

    def validate(self, attrs):
        """Along with the inherited auth token and refresh token, id of user,
        and entity are added into the response."""
        self.device_id = attrs.get("device_id", None)
        force_logout = attrs.get("force_logout", False)
        device_name = attrs.get("device_name", "")
        device_loc = attrs.get("device_loc", "")
        version = attrs.get("version", "")

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
        self._get_or_create_device(device_name, device_loc, version=version)

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

    def _get_or_create_device(self, device_name, device_loc, version=None):
        """Get or create device for user."""
        device, created = self.user.devices.get_or_create(
            registration_id=self.device_id, user=self.user
        )
        if not created:
            device.active = True
        device.device_name = device_name
        device.device_loc = device_loc
        if version:
            device.version = version
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
        expires_in = refresh.access_token.get("exp") - timezone.now().timestamp()
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
            user = CustomUser.objects.get(email=validated_data["email"], is_active=True)
            user.reset_password(ip, location, device)
        except CustomUser.DoesNotExist:
            raise exceptions.BadRequest(_("Email is not registered with any user"))
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
        validation_token = attrs.get("validation_token", {"object": None}).pop("object")
        if entity and not entity.entity_members.filter(user=user).exists():
            raise serializers.ValidationError(
                _("Member is removed or not available, please contact admin.")
            )
        if validation_token:
            if not user:
                raise serializers.ValidationError(
                    {
                        "validation_token": [
                            _("User ID is required to validate " "Validation Token")
                        ]
                    }
                )
            if (
                not user.password
                or not user.has_usable_password()
                or validation_token.type == acc_constants.ValidationTokenType.RESET_PASS
            ):
                attrs["validation_token"]["set_password"] = True
            if user != getattr(validation_token, "user", None):
                attrs["validation_token"]["value"] = "-"
                attrs["validation_token"]["valid"] = False
                attrs["validation_token"]["message"] = _("Invalid validation token")
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
            attrs["token"] = ValidationToken.objects.get(key=attrs.get("token"))
        except ValidationToken.DoesNotExist:
            raise exceptions.BadRequest(_("Token does not exist."))
        try:
            attrs["user"] = CustomUser.objects.get(id=attrs.get("user"))
        except CustomUser.DoesNotExist:
            raise exceptions.BadRequest(_("User does not exist"))
        if (
            attrs["user"].password
            and attrs["user"].has_usable_password()
            and attrs["token"].type != acc_constants.ValidationTokenType.RESET_PASS
        ):
            raise serializers.ValidationError(
                _("Password already set. " "User reset password to change password.")
            )
        if attrs.get("old_password", None) and not attrs["user"].check_password(
            attrs["old_password"]
        ):
            raise serializers.ValidationError(_("Password is incorrect."))
        if attrs["new_password1"] != attrs["new_password2"]:
            raise serializers.ValidationError(_("Your passwords didn't match."))
        return attrs

    def create(self, validated_data):
        """Create and return a new `User` instance, given the validated
        data."""
        super(PasswordResetConfirmSerializer, self).create(validated_data)
        user = validated_data["user"]
        user.set_password(validated_data["new_password1"])
        if validated_data["token"].type == acc_constants.ValidationTokenType.INVITE:
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


class AuthHandshakeSerializer(serializers.Serializer):
    """Serializer to validate and return token after logging in the user."""

    device_id = serializers.CharField(required=True)
    type = serializers.ChoiceField(choices=DeviceType, required=True)
    version = serializers.CharField(
        validators=[base_utils.validate_semantic_version], required=True
    )
    nonce = serializers.CharField(required=True)

    def get_device_info(self, validated_data):
        device_info = {
            "is_registered": False,
            "device_id": "",
            "type": "",
            "status": "not_registered",
        }
        device = UserDevice.objects.filter(
            registration_id=validated_data["device_id"],
            version=validated_data["version"],
            type=validated_data["type"],
        ).first()
        if device:
            device_info["is_registered"] = True
            device_info["device_id"] = device.registration_id
            device_info["type"] = device.type
            device_info["status"] = "active" if device.active else "deactivated"
        else:
            device_info["device_id"] = validated_data["device_id"]
            device_info["type"] = validated_data["type"]
        return device_info

    def validate_nonce(self, value):
        if auth_models.AuthSession.objects.filter(
            client_nonce=value
        ).exists():
            raise serializers.ValidationError(
                _(
                    "The provided nonce value is invalid. This nonce has already been used."
                )
            )
        return value

    @transaction.atomic
    def generate_session(self, client_nonce, device_id):
        """
        Create a new session by generating a server_nonce, session_token, and setting expiration.

        Args:
            client_nonce (str): The client's nonce sent during the handshake.

        Returns:
            dict: Contains the session token, client nonce, and server nonce.
        """
        # Set the session to expire after 15 minutes
        expires_at = datetime.now() + timedelta(days=1)

        # Store the session information in the database
        session = auth_models.AuthSession.objects.create(
            client_nonce=client_nonce, expires_at=expires_at, device_id=device_id
        )

        return {
            "session_token": session.session_token,
            "server_nonce": session.server_nonce,
            "expires_at": session.expires_at,
        }

    def to_representation(self, validated_data):
        response = {}
        response["device_info"] = self.get_device_info(validated_data)
        response["server_info"] = {
            "server_name": settings.SERVER_NAME,
            "server_version": base_utils.get_server_version(),
        }
        response["authentication_method"] = settings.CONNECT_AUTHENTICATION_METHOD
        response.update(self.generate_session(validated_data["nonce"], validated_data["device_id"]))
        response["security"] = settings.CONNECT_REQUEST_SECURITY_INFO
        return response


class UserDeviceSerializer(serializers.ModelSerializer):
    device_id = serializers.CharField(required=True, source="registration_id")
    type = serializers.ChoiceField(choices=DeviceType, required=True)
    version = serializers.CharField(
        validators=[base_utils.validate_semantic_version], required=True
    )
    id = fields.SerializableRelatedField(read_only=True)
    class Meta:
        model = UserDevice
        fields = (
            "id",
            "type",
            "device_id",
            "device_name",
            "device_loc",
            "active",
            "version"
        )

class AuthDeviceRegistrationSerializer(UserDeviceSerializer):
    """Serializer to validate and return token after logging in the user."""

    force_logout =  serializers.BooleanField(required=False)
    id = fields.SerializableRelatedField(read_only=True)
    device_name = serializers.CharField(required=True)
    device_id = serializers.CharField(required=True, source="registration_id")


    class Meta:
        model = UserDevice
        fields = (
            "id",
            "type",
            "device_id",
            "active",
            "version",
            "device_name",
            "device_loc",
            "force_logout"
        )

    def validate(self, attrs):
        attrs["user"] = auth_utils.get_current_user()
        session_device = auth_utils.get_session_device()
        if session_device != attrs["registration_id"]:
            raise serializers.ValidationError({"device_id": _("Invalid device_id.")})
        entity = attrs["user"].get_default_entity()
        if not entity.company.allow_multiple_login:
            if self.check_multiple_login(attrs):
                raise serializers.ValidationError({"device_id": _("User is already logged in another device.")})
        return super().validate(attrs)

    def create(self, validated_data):
        device, created = UserDevice.objects.get_or_create(
            registration_id=validated_data["registration_id"], user=validated_data["user"]
        )
        if not created:
            device.active = True
        device.device_name = validated_data["device_name"] if "device_name" in validated_data else ""
        device.device_loc = validated_data["device_loc"] if "device_loc" in validated_data else ""
        device.version = validated_data["version"]
        device.save()
        return device

    def check_multiple_login(self, attrs):
        """Check if user is already logged in on another device."""
        if "force_logout" in attrs and attrs["force_logout"]:
            UserDevice.deactivate_devices(attrs["user"])
        active_devices = UserDevice.active_devices(attrs["user"]).exclude(
            registration_id=attrs["registration_id"]
        )
        if active_devices.exists():
            return True
        return False

    def to_representation(self, instance):
        response =  super().to_representation(instance)
        response["user_id"] = instance.user.id
        entity = instance.user.get_default_entity()
        response["entity_id"] = ""
        if entity:
            response["entity_id"] = entity.id
        return response
