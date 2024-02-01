"""Customizations for API views."""
import re
from collections import defaultdict as dd

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


class IdDecodeModelViewSet(viewsets.ModelViewSet):
    """Viewset to decode id to normal id.

    This viewset is designed to handle decoding of hash IDs in the URL,
    using "hashid" as the lookup URL keyword and "id" as the lookup
    field.
    """

    lookup_url_kwarg = "hashid"
    lookup_field = "id"


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
