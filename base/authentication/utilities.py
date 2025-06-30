from django.utils.translation import gettext_lazy as _
from sentry_sdk import set_tag

from base.authentication.session import get_from_local, set_to_local
from base.exceptions import custom_exceptions as exceptions
from utilities.functions import decode


def get_current_user():
    """Returns the currently authenticated user when called while processing an
    API.

    Otherwise, returns None.
    """
    from django.contrib.auth import get_user_model

    UserModel = get_user_model()

    user = get_from_local("user", None)
    current_user = UserModel.objects.filter(id=get_from_local("user_id")).first()
    if user and user == current_user:
        return user
    user = current_user
    set_to_local("user", user)
    return user


def get_current_entity():
    """Returns the currently authenticated entity when called while processing
    an API.

    Otherwise, returns None.
    """
    from v1.supply_chains.models import Company

    entity = get_from_local("entity", None)
    current_entity = Company.objects.filter(id=get_from_local("entity_id")).first()
    if entity and entity == current_entity:
        return entity
    entity = current_entity
    set_to_local("entity", entity)
    return entity


def get_current_device():
    """Returns the currently authenticated device when called while processing
    an API.

    Otherwise, returns None.
    """
    from v1.accounts.models import UserDevice

    device = get_from_local("device", None)
    user = get_current_user()
    current_device = UserDevice.get_device_with_device_id(device, user)

    if current_device:
        return current_device
    return None

def get_session_device():
    """Returns the currently authenticated device while calling handshake.

    Otherwise, returns None.
    """

    return get_from_local("device", None)


class AuthMixin:

    def set_section(self, user, validated_token):
        """Set session data to local storage and tags based on the
        authentication method used.

        Args:
            user (User): The authenticated user.
            validated_token (dict): Validated token data.
        """
        session_data = {}
        if self.__class__.__name__ == "JWTAuthentication":
            session_data = {
                k: decode(v) if k.endswith("_id") else v
                for k, v in validated_token["session_data"].items()
            }

            # Check if the device associated with the user is active
            if not user.is_device_active(session_data["device"]):
                raise exceptions.AccessForbidden("Device deactivated login again.")
        elif self.__class__.__name__ == "OAuth2Authentication":
            session_data = {
                "user_id": user.id,
                "entity_id": validated_token.company_id,
            }
        elif self.__class__.__name__ == "SSOJWTAuthentication":
            from v1.supply_chains.models.company_models import CompanyMember

            entity = user.get_default_entity()
            if not entity:
                raise exceptions.AuthenticationFailed(
                    _("User does not have access any Entities")
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
            session_data = {
                "user_id": user.id.hashid,
                "entity_id": entity.id.hashid,
                "member_type": entity_member.type,
                "device": validated_token["device"]
            }

        # Set session data to local storage and tags
        for k, v in session_data.items():
            set_to_local(k, v)
            set_tag(f"session.{k}", v)
