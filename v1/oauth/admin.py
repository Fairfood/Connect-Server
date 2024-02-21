from django.contrib import admin
from oauth2_provider.admin import AccessTokenAdmin
from oauth2_provider.admin import ApplicationAdmin

from v1.oauth.models import ClientServerCompany

# Register your models here.


class ClientServerCompanyInline(admin.TabularInline):
    model = ClientServerCompany
    extra = 0


class ClientServerAdmin(ApplicationAdmin):
    inlines = (ClientServerCompanyInline,)


class ClientAccessTokenAdmin(AccessTokenAdmin):
    list_display = ("token", "user", "company", "application", "expires")
