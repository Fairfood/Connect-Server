from celery.result import AsyncResult
from django.contrib.auth import logout
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenRefreshView as SJWTTokenRefreshView,
)

from . import serializers as auth_serializers
from base.authentication import utilities as utils
from base.exceptions.custom_exceptions import BadRequest
from base.request_handler.response import SuccessResponse


# Create your views here.


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
