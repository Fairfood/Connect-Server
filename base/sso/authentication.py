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

from base.sso.settings import sso_settings

AUTH_HEADER_TYPES = sso_settings.AUTH_HEADER_TYPES

if not isinstance(sso_settings.AUTH_HEADER_TYPES, (list, tuple)):
    AUTH_HEADER_TYPES = (AUTH_HEADER_TYPES,)

AUTH_HEADER_TYPE_BYTES: Set[bytes] = {
    h.encode(HTTP_HEADER_ENCODING) for h in AUTH_HEADER_TYPES
}
from base.authentication import utilities as auth_utils

AuthUser = TypeVar("AuthUser", AbstractBaseUser, TokenUser)
from rest_framework.request import Request


class SSOJWTAuthentication(JWTAuthentication, auth_utils.AuthMixin):
    """
    An authentication plugin that authenticates requests through a JSON web
    token provided in a request header.
    """

    def authenticate(self, request: Request) -> Optional[Tuple[AuthUser, Token]]:
        header = self.get_header(request)
        if header is None:
            return None
        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None
        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token, request)
        session = self.get_user_session(request)
        self.set_section(
            user, {"token": validated_token, "device": self.get_device(session)}
        )
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
            from sentry_sdk import capture_exception

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
            self.validate_hmac_signature(auth_session, received_signature, request)
        return auth_session

    def get_device(self, session):
        return session.device_id
