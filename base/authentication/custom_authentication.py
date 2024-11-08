from importlib import import_module
from typing import Tuple, TypeVar

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from oauth2_provider.oauth2_backends import get_oauthlib_core
from rest_framework import authentication
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.models import TokenUser
from rest_framework_simplejwt.tokens import Token

from base.authentication.utilities import AuthMixin
from base.exceptions import custom_exceptions as exceptions

AuthUser = TypeVar("AuthUser", AbstractBaseUser, TokenUser)


class OAuth2Authentication(OAuth2Authentication, AuthMixin):
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
            self.set_section(r.user, r.access_token)
            return r.user, r.access_token
        request.oauth2_error = getattr(r, "oauth2_error", {})
        return None


class JWTAuthentication(JWTAuthentication, AuthMixin):
    """
    An authentication plugin that authenticates requests through a JSON web
    token provided in a request header.
    """

    def authenticate(self, request: Request) -> Tuple[AuthUser, Token] | None:
        auth_response = super().authenticate(request)
        if not auth_response:
            return auth_response
        user, validated_token = auth_response
        self.set_section(user, validated_token)
        return user, validated_token


class CustomDynamicAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class that dynamically selects and uses the appropriate
    authentication mechanism based on the `Auth-Type` header in the request.
    """

    def get_auth_class(self, auth_type):
        """
        Retrieves the authentication class based on the provided auth type.

        Args:
            auth_type (str): The type of authentication specified in the request header.

        Returns:
            Type: The authentication class corresponding to the auth type.

        Raises:
            AuthenticationFailed: If the provided auth type is not supported.
        """

        # Get the authentication class path from settings
        auth_class_path = settings.AUTH_TYPE_CLASSES.get(auth_type)
        if not auth_class_path:
            raise exceptions.AuthenticationFailed(
                f"Unsupported authentication type: {auth_type}"
            )
        # Split the path into module path and class name
        module_path, class_name = auth_class_path.rsplit(".", 1)

        # Import the module and get the class
        module = import_module(module_path)
        return getattr(module, class_name)

    def authenticate(self, request):
        """
        Dynamically selects and uses the appropriate authentication mechanism based on the
        `Auth-Type` header in the request. Calls the `authenticate` method of the selected
        authentication class.

        Args:
            request (HttpRequest): The HTTP request object containing the authentication data.

        Returns:
            tuple or None: A tuple of (user, auth) if authentication is successful, or None if not.
        """

        # Extract auth type from request header or default to 'password_grant'
        auth_type = request.headers.get("Auth-Type", "password_grant").lower()

        # Get the relevant authentication class
        auth_class = self.get_auth_class(auth_type)
        # Instantiate the authentication class and authenticate
        return auth_class().authenticate(request)
