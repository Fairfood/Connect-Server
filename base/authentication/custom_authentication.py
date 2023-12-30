from rest_framework_simplejwt.authentication import JWTAuthentication
from sentry_sdk import set_tag

from base.authentication.session import set_to_local
from base.exceptions import custom_exceptions as exceptions
from utilities.functions import decode


class CustomAuthentication(JWTAuthentication):
    """Authentication class customized to set session data to thread local
    storage."""

    def authenticate(self, request):
        """Call the default authentication mechanism to validate the token and
        fetch the user.

        Then, additional session data received in the token is set to
        thread local storage. All session variables included, will be
        sent as tag to sentry.
        """
        user_token = super(CustomAuthentication, self).authenticate(request)
        if not user_token:
            return None
        user, validated_token = user_token

        session_data = {
            k: decode(v) if k.endswith("_id") else v
            for k, v in validated_token["session_data"].items()
        }

        if not user.is_device_active(session_data["device"]):
            raise exceptions.AccessForbidden("Device deactivated login again.")

        for k, v in session_data.items():
            set_to_local(k, v)
            set_tag(f"session.{k}", v)
        return user, validated_token
