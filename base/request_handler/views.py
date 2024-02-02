"""Customizations for API views."""
import re
from collections import defaultdict as dd
from typing import Any

from django.db import models
from rest_framework import viewsets
from rest_framework.views import APIView

from base.request_handler.response import SuccessResponse


class IDEncodeLookupMixin:
    """Use this mixin for Viewsets to use hash ID in the URL.

    This mixin modifies the get_object method to handle hash IDs in the
    URL.
    """

    def get_object(self):
        """Retrieve and return an object from the queryset.

        If 'id' is present in self.kwargs and it's not a numeric string,
        assume it's a hash ID and use it.

        Returns:
            The retrieved object.
        """
        if "id" in self.kwargs and not str(self.kwargs["id"].isdigit()):
            self.kwargs["id"] = self.kwargs["id"]
        return super(IDEncodeLookupMixin, self).get_object()


class IDDecodeViewSetMixin:
    """Viewset to decode id to normal id.

    This viewset is designed to handle decoding of hash IDs in the URL,
    using "hashid" as the lookup URL keyword and "id" as the lookup
    field.
    """

    lookup_url_kwarg = "hashid"
    lookup_field = "id"


class OAuthScopeViewSetMixin:
    """Mixin class for providing OAuth scope information for a Django REST
    framework viewset.

    Attributes:
        resource_types (list): List of resource types associated with the
                               viewset.

    Methods:
        get_required_alternate_scopes(): Get required alternate OAuth scopes
            based on HTTP methods and resource types.
    """

    resource_types = []

    def get_required_alternate_scopes(self):
        """Get the required alternate OAuth scopes based on HTTP methods and
        resource types.

        Returns:
            dict: A dictionary mapping HTTP methods to lists of alternate OAuth
                scopes.
        """
        required_scopes = {}
        method_scopes_mapping = {
            "GET": "read",
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete",
        }

        for method in self.http_method_names:
            upper_method = method.upper()
            if upper_method in method_scopes_mapping:
                required_scopes[upper_method] = [
                    [
                        f"{method_scopes_mapping[upper_method]}:"
                        f"{resource_type}"
                        for resource_type in self.resource_types
                    ]
                ]

        return required_scopes


class IDDEcodeScopeViewset(
    IDDecodeViewSetMixin, OAuthScopeViewSetMixin, viewsets.ModelViewSet
):
    """Viewset combining ID decoding, OAuth scope information, and Django REST
    framework's ModelViewSet.

    This viewset inherits from `IDDecodeViewSetMixin` for ID decoding,
    `OAuthScopeViewSetMixin` for providing OAuth scope information, and
    `viewsets.ModelViewSet` for typical model viewset functionality.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.required_alternate_scopes = self.get_required_alternate_scopes()


class Constants(APIView):
    """API to return configurations.

    API lists al the configurations constants defined across the apps.
    """

    permission_classes = []

    def get(self, request, *args, **kwargs):
        """Returns the list of constants used across the apps, categorized by
        app name."""
        constant_config = dd(lambda: dd(list))
        for defined_choices in models.IntegerChoices.__subclasses__():
            app_name = defined_choices.__module__.split(".")[1]
            choice_name = re.sub(
                r"(?<!^)(?=[A-Z])", "_", defined_choices.__name__
            ).lower()
            constant_config[app_name][choice_name] = [
                {"name": choice[1], "id": choice[0]}
                for choice in defined_choices.choices
            ]
        return SuccessResponse(constant_config)
