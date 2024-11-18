"""trace_connect URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, register_converter
from django_otp.admin import OTPAdminSite
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from base.request_handler import converters
from base.request_handler import views as base_views

if settings.ENVIRONMENT == "production":
    admin.site.__class__ = OTPAdminSite

register_converter(converters.IDConverter, "hashid")

schema_view = get_schema_view(
    openapi.Info(
        title="Trace Connect API",
        default_version="v1",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("connect/admin/", admin.site.urls),
    path(
        "connect/v1/constants/",
        base_views.Constants.as_view(),
        name="constants",
    ),
    path("connect/v1/auth/", include("v1.apiauth.urls")),
    path("connect/v1/accounts/", include("v1.accounts.urls")),
    path("connect/v1/notifications/", include("v1.notifications.urls")),
    path("connect/v1/supply-chains/", include("v1.supply_chains.urls")),
    path("connect/v1/catalogs/", include("v1.catalogs.urls")),
    path("connect/v1/transactions/", include("v1.transactions.urls")),
    path("connect/v1/forms/", include("v1.forms.urls")),
    path("connect/v1/oauth/", include("v1.oauth.urls")),
]

if settings.DEBUG and settings.ENVIRONMENT in ["development", "local"]:
    urlpatterns += (
        path(
            "connect/v1/",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
    )
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
