import base64
import hashlib
import hmac
from typing import Optional, Set, Tuple, TypeVar

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from rest_framework import HTTP_HEADER_ENCODING
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import (AuthenticationFailed,
                                                 InvalidToken, TokenError)
from rest_framework_simplejwt.models import TokenUser
from rest_framework_simplejwt.tokens import Token

from base.exceptions import custom_exceptions as exceptions
from base.sso.settings import sso_settings

AUTH_HEADER_TYPES = sso_settings.AUTH_HEADER_TYPES

if not isinstance(sso_settings.AUTH_HEADER_TYPES, (list, tuple)):
    AUTH_HEADER_TYPES = (AUTH_HEADER_TYPES,)

AUTH_HEADER_TYPE_BYTES: Set[bytes] = {
    h.encode(HTTP_HEADER_ENCODING) for h in AUTH_HEADER_TYPES
}
from sentry_sdk import capture_exception, capture_message

from base.authentication import utilities as auth_utils

AuthUser = TypeVar("AuthUser", AbstractBaseUser, TokenUser)
from rest_framework.request import Request


class SSOJWTAuthentication(JWTAuthentication, auth_utils.AuthMixin):
    """
    An authentication plugin that authenticates requests through a JSON web
    token provided in a request header.
    """

    def authenticate(self, request: Request) -> Optional[Tuple[AuthUser, Token]]:
        # Get the authorization header from the request
        header = self.get_header(request)
        if header is None:
            return None  # No authorization header found

        # Extract the raw token from the header
        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None  # No token found in the header

        # Validate the raw token
        validated_token = self.get_validated_token(raw_token)

        # Get the user associated with the validated token
        user = self.get_user(validated_token, request)

        # Get the user session
        session = self.get_user_session(request)

        # Get the device ID from the session
        device_id = self.get_device(session)

        # Validate the device associated with the request and user
        self.validate_device(request, device_id, user)

        # Set user session information with token and device details
        self.set_section(user, {"token": validated_token, "device": device_id})
        return user, validated_token

    def get_validated_token(self, raw_token: bytes) -> Token:
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        messages = []
        for AuthToken in sso_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except TokenError as e:
                messages.append(
                    {
                        "token_class": AuthToken.__name__,
                        "token_type": AuthToken.token_type,
                        "message": e.args[0],
                    }
                )

        raise InvalidToken(
            {
                "detail": _("Given token not valid for any token type"),
                "messages": messages,
            }
        )

    def get_header(self, request: Request) -> bytes:
        """
        Extracts the header containing the JSON web token from the given
        request.
        """
        header = request.META.get(sso_settings.AUTH_HEADER_NAME)

        if isinstance(header, str):
            # Work around django test client oddness
            header = header.encode(HTTP_HEADER_ENCODING)

        return header

    def get_user(self, validated_token: Token, request: Request) -> AuthUser:
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[sso_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(_("Token contained no recognizable user identification"))
        try:
            user = self.user_model.objects.get(**{sso_settings.USER_ID_FIELD: user_id})
        except self.user_model.DoesNotExist:
            raise AuthenticationFailed(_("User not found"), code="user_not_found")

        if not user.is_active:
            raise AuthenticationFailed(_("User is inactive"), code="user_inactive")
        return user

    def validate_hmac_signature(
        self, auth_session, received_signature, request: Request
    ) -> bool:
        """
        Validate the HMAC signature from the incoming request.

        Args:
            request: Django request object containing headers and body.

        Returns:
            bool: True if HMAC signature is valid, False otherwise.
        """
        try:
            # Get the request body and convert it to bytes
            body = (
                request.body
                if isinstance(request.body, bytes)
                else request.body.encode("utf-8")
            )

            # Create a new HMAC object using the secret key and request body
            hmac_obj = hmac.new(
                auth_session.session_token.encode(), body, hashlib.sha256
            )

            # Base64 encode the resulting HMAC digest
            computed_signature = base64.b64encode(hmac_obj.digest()).decode()

            # Compare the received signature with the computed one (timing-safe comparison)
            if not hmac.compare_digest(computed_signature, received_signature):
                raise AuthenticationFailed(
                    "HMAC validation failed: Signature mismatch."
                )

            return True  # HMAC validation successful
        except Exception as e:
            capture_exception(e)
            raise AuthenticationFailed(
                "HMAC validation failed: An unexpected error occurred during validation."
            )

    def get_user_session(self, request: Request):

        # Extract HMAC signature, client nonce, and server nonce from headers
        client_nonce = request.headers.get("Client-Nonce")
        server_nonce = request.headers.get("Server-Nonce")

        if not client_nonce or not server_nonce:
            raise AuthenticationFailed(
                "'Client-Nonce' and 'Server-Nonce' headers are required"
            )

        # Fetch the session token using client_nonce and server_nonce
        from v1.apiauth.models import AuthSession

        auth_session = AuthSession.objects.filter(
            client_nonce=client_nonce, server_nonce=server_nonce
        ).first()

        if not auth_session:
            raise AuthenticationFailed(
                "HMAC validation failed: No matching session found for the provided nonces."
            )
        if settings.VALIDATE_HMAC_SIGNATURE:
            # Skip HMAC validation for GET requests
            if request.method.lower() == "get":
                return True  # GET requests are not validated with HMAC

            received_signature = request.headers.get("HMAC-Signature")
            if not received_signature:
                raise AuthenticationFailed(
                    "HMAC validation failed: 'HMAC-Signature' header required"
                )

            # Access the view instance from the request context
            view = request.parser_context.get("view", None)

            # Validate signature only if the view has 'validate_payload_signature' set to True
            if view and getattr(view, "validate_payload_signature", False):
                self.validate_hmac_signature(auth_session, received_signature, request)
        return auth_session

    def get_device(self, session):
        """
        Get the device ID from the session.

        Args:
            session: The user session object.

        Returns:
            The device ID associated with the session.
        """
        return session.device_id

    def validate_device(self, request, device_id, user):
        """
        Validate the device making the request to ensure it is an authorized device for the user.

        Args:
            request: The Django request object.
            device_id: The device ID extracted from the session.
            user: The authenticated user object.

        Raises:
            AuthenticationFailed: If the device validation fails.
        """
        from v1.accounts.models import UserDevice

        # Access the view instance from the request context
        view = request.parser_context.get("view", None)

        # Skip device validation if the view has 'exclude_device_validation' set to True
        if view and getattr(view, "exclude_device_validation", False):
            return

        # Retrieve the device associated with the user and device ID
        logged_device = UserDevice.get_device_with_device_id(device_id, user)

        # Raise an authentication failure if no valid device is found
        if not logged_device:
            self.log_device_auth_failure(user, device_id)
            raise AuthenticationFailed("Device authentication failed")

        # Raise an authentication failure if device is inactive
        if not logged_device.active:
            raise exceptions.AccessForbidden("Device deactivated login again.")

    def log_device_auth_failure(self, user, device_id):
        """
        Log an authentication failure due to device validation.

        Args:
            user: The user attempting to authenticate.
            device_id: The device ID that failed validation.
        """

        capture_message(
            f"Device authentication failed for user {user.id} with device ID {device_id}"
        )
