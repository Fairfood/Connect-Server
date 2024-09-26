"""URLs of the authentication."""
from dj_rest_auth import views as dj_rest_auth_views
from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView

from . import views

urlpatterns = [
    # Authentication APIS
    path("login/", views.LoginView.as_view(), name="login"),
    path("handshake/", views.AuthHandshakeView.as_view(), name="handshake"),
    path("device/registration/", views.AuthDeviceRegisterView.as_view(), name="device_registration"),
    path("devices/", views.UserDeviceView.as_view(), name="device_registration"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path(
        "token/refresh/",
        views.TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path(
        "validate/",
        views.ValidationView.as_view(),
        name="validation_token_verify",
    ),
    path(
        "password/change/",
        dj_rest_auth_views.PasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "password/reset/",
        views.ResetPasswordView.as_view(),
        name="password_reset",
    ),
    path(
        "password/reset/confirm/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password/check/",
        views.CheckPasswordView.as_view(),
        name="check_password",
    ),
    path(
        "trace/sync-status/",
        views.TraceSyncView.as_view(),
        name="trace-sync-status",
    ),
]
