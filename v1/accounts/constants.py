"""Constants under the user accounts section are stored here."""
from django.db import models
from django.utils.translation import gettext_lazy as _


# Validity in Minutes
_30_MINUTES = 30  # 30 Minutes
_1_DAY = 1440  # 24 hours
_2_DAY = 2880  # 48 hours
_365_DAYS = 525600  # 365 days


class Language(models.TextChoices):
    """Enumeration of supported languages.

    Provides choices for language selection in the application.
    """

    ENGLISH = "en", _("English")
    DUTCH = "nl", _("Dutch")
    GERMAN = "de", _("German")
    FRENCH = "fr", _("French")


class UserType(models.IntegerChoices):
    """Enumeration of user types.

    Represents different types of users in the application.
    """

    SUPER_ADMIN = 101, _("Super Admin")
    ADMIN = 111, _("Admin")
    ENTITY_USER = 121, _("Entity User")


class UserStatus(models.IntegerChoices):
    """Enumeration of user status.

    Represents different status values for user accounts.
    """

    CREATED = 101, _("User Created")
    ACTIVE = 111, _("User Active")


class ValidationTokenStatus(models.IntegerChoices):
    """Enumeration of validation token status.

    Represents the status of validation tokens used in the application.
    """

    USED = 101, _("Used")
    UNUSED = 111, _("Unused")


class ValidationTokenType(models.IntegerChoices):
    """Enumeration of validation token types.

    Represents different types of validation tokens used in the
    application.
    """

    VERIFY_EMAIL = 101, _("Verify Email")
    CHANGE_EMAIL = 102, _("Change Email")
    RESET_PASS = 103, _("Reset Password")
    OTP = 104, _("OTP")
    MAGIC_LOGIN = 105, _("Magic Login")
    INVITE = 106, _("Invite")
    NOTIFICATION = 107, _("Notification")


class DeviceType(models.IntegerChoices):
    """Enumeration of device types.

    Represents different types of devices supported by the application.
    """

    ANDROID = 101, _("Android")
    IOS = 102, _("Ios")
    WEB = 103, _("Web")


MOBILE_DEVICE_TYPES = [DeviceType.ANDROID, DeviceType.IOS]


# Validity
TOKEN_VALIDITY = {
    ValidationTokenType.VERIFY_EMAIL: _365_DAYS,
    ValidationTokenType.CHANGE_EMAIL: _365_DAYS,
    ValidationTokenType.RESET_PASS: _2_DAY,
    ValidationTokenType.OTP: _30_MINUTES,
    ValidationTokenType.MAGIC_LOGIN: _2_DAY,
    ValidationTokenType.INVITE: _365_DAYS,
    ValidationTokenType.NOTIFICATION: _365_DAYS,
}
