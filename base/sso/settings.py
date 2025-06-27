from datetime import timedelta
from typing import Any, Dict

from django.conf import settings
from django.test.signals import setting_changed
from django.utils.translation import gettext_lazy as _
from rest_framework.settings import APISettings as _APISettings

USER_SETTINGS = getattr(settings, "SSO_AUTH", None)

DEFAULTS = {
    "ALGORITHM": "HS256",
    "SIGNING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "email",
    "USER_ID_CLAIM": "email",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("base.sso.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": None,
    "JTI_CLAIM": "jti",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "VERFIFICATION_FILE_PATH": None

}

IMPORT_STRINGS = (
    "AUTH_TOKEN_CLASSES",
    "JSON_ENCODER",
    "USER_AUTHENTICATION_RULE",
)

REMOVED_SETTINGS = ()


class APISettings(_APISettings):  # pragma: no cover
    def __check_user_settings(self, user_settings: Dict[str, Any]) -> Dict[str, Any]:
        SETTINGS_DOC = ""
        for setting in REMOVED_SETTINGS:
            if setting in user_settings:
                raise RuntimeError(
                    "The '%s' setting has been removed. Please refer to '%s' for available settings."
                    % (setting, SETTINGS_DOC)
                )

        return user_settings


sso_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)


def reload_api_settings(*args, **kwargs) -> None:  # pragma: no cover
    global api_settings

    setting, value = kwargs["setting"], kwargs["value"]

    if setting == "SSO_AUTH":
        api_settings = APISettings(value, DEFAULTS, IMPORT_STRINGS)


setting_changed.connect(reload_api_settings)
