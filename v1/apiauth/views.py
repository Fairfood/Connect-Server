from urllib import request

from celery.result import AsyncResult
from django.contrib.auth import logout
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (TokenBlacklistView,
                                            TokenObtainPairView)
from rest_framework_simplejwt.views import \
    TokenRefreshView as SJWTTokenRefreshView
from sentry_sdk import capture_exception

from base.authentication import utilities as utils
from base.exceptions.custom_exceptions import BadRequest
from base.request_handler.response import SuccessResponse
# Create your views here.
from v1.accounts.models import UserDevice

from . import serializers as auth_serializers


class LoginView(TokenObtainPairView):
    """API to login User.

    Takes in Email and password to login user with a session.
    """

    serializer_class = auth_serializers.APILoginSerializer


class LogoutView(APIView):
    """API to logout User.

    Takes in Email and password to logout user with a session.
    """

    def post(self, request, *args, **kwargs):
        """Get method for logging in user."""
        device = utils.get_current_device()
        if device:
            device.deactivate()
        from django.conf import settings
        if settings.SSO_ENABLED == "1":
            from base.sso.settings import sso_settings
            if self.request.auth.__class__ in  sso_settings.AUTH_TOKEN_CLASSES:
                from base.sso.tokens import AccessToken
                token_class = AccessToken
                access = token_class(self.request.auth.token)
                try:
                    access.blacklist()
                except AttributeError as e:
                    print(e)
                    capture_exception(e)
        else:
            logout(request)
        return SuccessResponse("Logged out successfully.")


class TokenRefreshView(SJWTTokenRefreshView):
    """API to Refresh Token.

    Takes in the refresh token to provide a new Refresh and Access.
    Refresh token is refreshed to ensure that the user is only logged
    out if inactive for a long time
    """

    serializer_class = auth_serializers.TokenRefreshSerializer


class ResetPasswordView(generics.CreateAPIView):
    """API to reset user password.

    Open API to reset user's password. An email will be sent to the
    email ID to verify and reset the password
    """

    permission_classes = ()
    authentication_classes = ()

    serializer_class = auth_serializers.APIPasswordResetSerializer


class ValidationView(generics.CreateAPIView):
    """API to verify Validate Email, password or Token.

    This API can be used to validate any of Email-ID, Password or Validation
    token.

    Email and password fields are optional and can be sent alone.

    For validating Validation token, user id received in the url should also be
    supplied.
    """

    permission_classes = ()
    authentication_classes = ()

    serializer_class = auth_serializers.ValidationSerializer


class PasswordResetConfirmView(generics.CreateAPIView):
    """API to set user password.

    Takes in the validation token and other information to change the
    user's password after validating the validation token
    """

    permission_classes = ()
    authentication_classes = ()

    serializer_class = auth_serializers.PasswordResetConfirmSerializer


class CheckPasswordView(generics.CreateAPIView):
    """Api to check user password.

    By taking the password as a parameter checks the password is belong
    the logged-in user.
    """

    serializer_class = auth_serializers.CheckPasswordSerializer


class TraceSyncView(APIView):
    """Api view for syncing trace data."""

    def post(self, request, *args, **kwargs):
        """Get method for syncing trace data."""
        task_id = request.data.get("task_id", None)
        if not task_id:
            raise BadRequest("Task id is required.")
        try:
            result = AsyncResult(task_id)
            data = {
                "task_id": task_id,
                "status": result.status,
                "result": result.result,
            }
        except Exception:
            raise BadRequest("Check your task id.")
        return SuccessResponse(data)


class AuthHandshakeView(generics.CreateAPIView):
    """
    API View to handle the initial authentication handshake between
    the client (mobile/web app) and the server. This handshake provides
    authentication options and returns server-related information like
    nonce and session tokens for enhanced security.
    """
    serializer_class = auth_serializers.AuthHandshakeSerializer
    permission_classes = []
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        """
        Handle the POST request for the handshake. It validates the incoming
        request data using the specified serializer and returns a success response
        with the serialized data (e.g., authentication methods, server info, etc.).

        Args:
            request: The incoming request object containing device/app info.
            *args, **kwargs: Additional arguments for the view.

        Returns:
            SuccessResponse: A JSON response with the validated handshake data.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return SuccessResponse(serializer.data)


class AuthDeviceRegisterView(generics.CreateAPIView):
    """
    API View to handle the initial authentication handshake between
    the client (mobile/web app) and the server. This handshake provides
    authentication options and returns server-related information like
    nonce and session tokens for enhanced security.
    """
    serializer_class = auth_serializers.AuthDeviceRegistrationSerializer
    exclude_device_validation = True

    def post(self, request, *args, **kwargs):
        """
        Handle the POST request for the handshake. It validates the incoming
        request data using the specified serializer and returns a success response
        with the serialized data (e.g., authentication methods, server info, etc.).

        Args:
            request: The incoming request object containing device/app info.
            *args, **kwargs: Additional arguments for the view.

        Returns:
            SuccessResponse: A JSON response with the validated handshake data.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return SuccessResponse(serializer.data)


class UserDeviceView(generics.ListAPIView):
    """
    API View to handle the initial authentication handshake between
    the client (mobile/web app) and the server. This handshake provides
    authentication options and returns server-related information like
    nonce and session tokens for enhanced security.
    """
    serializer_class = auth_serializers.UserDeviceSerializer
    queryset = UserDevice.objects.all()

    def get_queryset(self):
        qs =  super().get_queryset()
        return qs.filter(user__id=self.request.user.pk)
