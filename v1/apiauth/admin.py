# from django.contrib import admin
# Register your models here.
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from base.db.admin import BaseAdmin

from .models import AuthSession


class AuthSessionAdmin(BaseAdmin):
    list_display = ("id", "session_token", "client_nonce", "server_nonce", "expires_at")

admin.site.register(AuthSession, AuthSessionAdmin)