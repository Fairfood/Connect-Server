from datetime import datetime, timedelta
from typing import Any, Dict, Optional, TypeVar

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenBackendError, TokenError
from rest_framework_simplejwt.models import TokenUser
from rest_framework_simplejwt.token_blacklist.models import (BlacklistedToken,
                                                             OutstandingToken)
from rest_framework_simplejwt.tokens import BlacklistMixin, Token
from rest_framework_simplejwt.utils import aware_utcnow, datetime_from_epoch

from base.sso.settings import sso_settings

AuthUser = TypeVar("AuthUser", AbstractBaseUser, TokenUser)

class BlacklistMixin:
    """
    If the `rest_framework_simplejwt.token_blacklist` app was configured to be
    used, tokens created from `BlacklistMixin` subclasses will insert
    themselves into an outstanding token list and also check for their
    membership in a token blacklist.
    """

    payload: Dict[str, Any]

    if "rest_framework_simplejwt.token_blacklist" in settings.INSTALLED_APPS:

        def verify(self, *args, **kwargs) -> None:
            self.check_blacklist()

        def check_blacklist(self) -> None:
            """
            Checks if this token is present in the token blacklist.  Raises
            `TokenError` if so.
            """
            jti = self.payload[sso_settings.JTI_CLAIM]
            if BlacklistedToken.objects.filter(token__jti=jti).exists():
                raise TokenError(_("Token is blacklisted"))

        def blacklist(self) -> BlacklistedToken:
            """
            Ensures this token is included in the outstanding token list and
            adds it to the blacklist.
            """
            jti = self.payload[sso_settings.JTI_CLAIM]
            exp = self.payload["exp"]

            # Ensure outstanding token exists with given jti
            token, created = OutstandingToken.objects.get_or_create(
                jti=jti,
                defaults={
                    "token": str(self),
                    "expires_at": datetime_from_epoch(exp),
                },
            )

            return BlacklistedToken.objects.get_or_create(token=token)

        @classmethod
        def for_user(cls, user: AuthUser) -> Token:
            """
            Adds this token to the outstanding token list.
            """
            token = super().for_user(user)  # type: ignore

            jti = token[sso_settings.JTI_CLAIM]
            exp = token["exp"]

            OutstandingToken.objects.create(
                user=user,
                jti=jti,
                token=str(token),
                created_at=token.current_time,
                expires_at=datetime_from_epoch(exp),
            )

            return token


class AccessToken(BlacklistMixin, Token):
    token_type = "access"
    lifetime = sso_settings.ACCESS_TOKEN_LIFETIME
    _token_backend: Optional["TokenBackend"] = None

    def __init__(self, token: Optional["Token"] = None, verify: bool = True) -> None:
        """
        !!!! IMPORTANT !!!! MUST raise a TokenError with a user-facing error
        message if the given token is invalid, expired, or otherwise not safe
        to use.
        """
        if self.token_type is None or self.lifetime is None:
            raise TokenError(_("Cannot create token with no type or lifetime"))

        self.token = token
        self.current_time = aware_utcnow()

        # Set up token
        if token is not None:
            # An encoded token was provided
            token_backend = self.get_token_backend()

            # Decode token
            try:
                self.payload = token_backend.decode(token, verify=verify)
            except TokenBackendError:
                raise TokenError(_("Token is invalid or expired"))

            if verify:
                self.verify()
        else:
            # New token.  Skip all the verification steps.
            self.payload = {sso_settings.TOKEN_TYPE_CLAIM: self.token_type}

            # Set "exp" and "iat" claims with default value
            self.set_exp(from_time=self.current_time, lifetime=self.lifetime)
            self.set_iat(at_time=self.current_time)

            # Set "jti" claim
            self.set_jti()

    def __str__(self) -> str:
        """
        Signs and returns a token as a base64 encoded string.
        """
        if isinstance(self.token, bytes):
            return self.token.decode("utf-8")
        return self.token

    @property
    def token_backend(self) -> "TokenBackend":
        if self._token_backend is None:
            self._token_backend = import_string(
                "base.sso.state.token_backend"
            )
        return self._token_backend

    def verify(self) -> None:
        """
        Performs additional validation steps which were not performed when this
        token was decoded.  This method is part of the "public" API to indicate
        the intention that it may be overridden in subclasses.
        """
        # According to RFC 7519, the "exp" claim is OPTIONAL
        # (https://tools.ietf.org/html/rfc7519#section-4.1.4).  As a more
        # correct behavior for authorization tokens, we require an "exp"
        # claim.  We don't want any zombie tokens walking around.
        self.check_exp()

        # If the defaults are not None then we should enforce the
        # requirement of these settings.As above, the spec labels
        # these as optional.
        if (
            sso_settings.JTI_CLAIM is not None
            and sso_settings.JTI_CLAIM not in self.payload
        ):
            raise TokenError(_("Token has no id"))

        if sso_settings.TOKEN_TYPE_CLAIM is not None:
            self.verify_token_type()

        BlacklistMixin.verify(self)

    @classmethod
    def for_user(cls, user: AuthUser) -> "Token":
        """
        Returns an authorization token for the given user that will be provided
        after authenticating the user's credentials.
        """
        user_id = getattr(user, sso_settings.USER_ID_FIELD)
        if not isinstance(user_id, int):
            user_id = str(user_id)

        token = cls()
        token[sso_settings.USER_ID_CLAIM] = user_id

        return token