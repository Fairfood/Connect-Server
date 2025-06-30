import pyotp
from django.conf import settings
from django.utils.timezone import activate as activate_timezone
from django.utils.translation import activate as activate_translation
from rest_framework import permissions
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from base.exceptions.custom_exceptions import BadRequest, AuthenticationFailed
from base.sso.settings import sso_settings


class CombinedPermission(permissions.BasePermission):
    """This permission class checks the type of authentication token in the
    request and delegates permission checks to the appropriate permission class
    based on the token type.

    Methods:
        has_permission(request, view): Check if the user has permission to
            access the view.
        has_object_permission(request, view, obj): Check if the user has
            permission to perform the action on the object.
    """

    def has_permission(self, request, view):
        """Check if the user has permission to access the view.

        Args:
            request (HttpRequest): The HTTP request being checked for
                permission.
            view (View): The Django REST framework view being accessed.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        permission = self.permission(request)
        return permission.has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        """Check if the user has permission to perform the action on the
        object.

        Args:
            request (HttpRequest): The HTTP request being checked for
                permission.
            view (View): The Django REST framework view being accessed.
            obj (object): The object being acted upon.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        permission = self.permission(request)
        return permission.has_object_permission(request, view, obj)

    def permission(self, request):
        """Get the appropriate permission class based on the authentication
        token type.

        Args:
            request (HttpRequest): The HTTP request being checked for
                permission.
        """
        token = request.auth
        # if not token:
        #     return False

        if token.__class__ in jwt_settings.AUTH_TOKEN_CLASSES:
            return permissions.IsAuthenticated()
        elif settings.SSO_ENABLED == "1" and token.__class__ in sso_settings.AUTH_TOKEN_CLASSES:
            return permissions.IsAuthenticated()
        else:
            from oauth2_provider.contrib.rest_framework import \
                TokenMatchesOASRequirements

            return TokenMatchesOASRequirements()


class BaseTOTP(permissions.BasePermission):
    """
    Base permission class for checking Time-Based One-Time Password (TOTP)
    authentication.

    This base permission class is used for checking TOTP authentication. It
    provides a `has_permission` method that checks the validity of the TOTP
    against the stored secret.

    Attributes:
    - otp_secret: The TOTP secret. This should be overridden in derived
        classes.

    Methods:
    - has_permission(request, view): Checks the TOTP validity.

    Example Usage:
    ```
    class MyTOTP(BaseTOTP):
        # Custom configurations and methods can be added here
        otp_secret = "xxx"
    ```
    """

    otp_secret = None

    def has_permission(self, request, view):
        """To check totp."""
        if settings.ENVIRONMENT == "local":
            return True
        
        if not self.otp_secret:
            raise AuthenticationFailed("Failed OTP.", send_to_sentry=False)
        
        current_otp = request.META.get("HTTP_OTP")
        if not current_otp:
            raise BadRequest(
                "Can not find OTP in the request header.", 
                send_to_sentry=False
            )
        
        timezone_str = request.META.get("HTTP_TIMEZONE", None)
        language_str = request.META.get("HTTP_LANGUAGE", None)
        if timezone_str:
            activate_timezone(timezone_str)
        if language_str:
            activate_translation(language_str)
        
        view.kwargs["language"] = language_str
        totp = pyotp.TOTP(self.otp_secret)
        if totp.verify(current_otp, valid_window=1):
            return True
        
        raise AuthenticationFailed("Invalid OTP.", send_to_sentry=False)


class ValidTOTP(BaseTOTP):
    """
    Derived permission class for checking TOTP authentication during
    validation.

    This permission class is used for checking TOTP authentication
    during validation. It inherits from the BaseTOTP class and sets the
    otp_secret to the TOTP token specified in the Django settings.
    """

    otp_secret = settings.TOTP_TOKEN