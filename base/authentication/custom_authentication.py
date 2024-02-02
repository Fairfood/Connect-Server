from django.conf import settings
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from oauth2_provider.oauth2_backends import get_oauthlib_core
from rest_framework import authentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from sentry_sdk import set_tag

from base.authentication.session import set_to_local
from base.exceptions import custom_exceptions as exceptions
from utilities.functions import decode


class ExtendedOAuth2Authentication(OAuth2Authentication):
    """Custom OAuth2 authentication class with extended functionality.

    This class extends the default OAuth2Authentication to provide
    additional features.
    """

    def authenticate(self, request):
        """Returns two-tuple of (user, token) if authentication succeeds, or
        None otherwise."""
        oauthlib_core = get_oauthlib_core()

        # Adding default scope for
        valid, r = oauthlib_core.verify_request(
            request, scopes=[settings.OAUTH2_PROVIDER_AUTH_SCOPE]
        )
        if valid:
            return r.user, r.access_token
        request.oauth2_error = getattr(r, "oauth2_error", {})
        return None


class CombinedAuthentication(authentication.BaseAuthentication):
    """Custom authentication class combining JWTAuthentication and
    ExtendedOAuth2Authentication.

    This authentication class first attempts to authenticate using
    JWTAuthentication. If the token is invalid, it switches to
    ExtendedOAuth2Authentication and retries authentication.

    Args:
        request (HttpRequest): The HTTP request to be authenticated.

    Returns:
        tuple: A tuple containing user and validated token if authentication is
              successful, or None if authentication fails.
    """

    authentication = JWTAuthentication()

    def authenticate(self, request):
        """Authenticate the user based on the provided request.

        Args:
            request (HttpRequest): The HTTP request to be authenticated.

        Returns:
            tuple: A tuple containing user and validated token if
                   authentication is successful, or None if authentication
                   fails.
        """

        try:
            user_token = self.authentication.authenticate(request)
        except InvalidToken:
            # Switch to ExtendedOAuth2Authentication if JWTAuthentication fails
            self.authentication = ExtendedOAuth2Authentication()
            user_token = self.authentication.authenticate(request)

        if not user_token:
            return None

        user, validated_token = user_token
        self.set_section(user, validated_token)
        return user, validated_token

    def set_section(self, user, validated_token):
        """Set session data to local storage and tags based on the
        authentication method used.

        Args:
            user (User): The authenticated user.
            validated_token (dict): Validated token data.
        """
        if self.authentication.__class__ == JWTAuthentication:
            session_data = {
                k: decode(v) if k.endswith("_id") else v
                for k, v in validated_token["session_data"].items()
            }

            # Check if the device associated with the user is active
            if not user.is_device_active(session_data["device"]):
                raise exceptions.AccessForbidden(
                    "Device deactivated login again."
                )
        else:
            session_data = {
                "user_id": user.id,
                "entity_id": validated_token.company_id,
            }

        # Set session data to local storage and tags
        for k, v in session_data.items():
            set_to_local(k, v)
            set_tag(f"session.{k}", v)
