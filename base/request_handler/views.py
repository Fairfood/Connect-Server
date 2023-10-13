"""Customizations for API views."""
import re
from collections import defaultdict as dd

from django.db import models
from rest_framework import viewsets
from rest_framework.views import APIView

from base.request_handler.response import SuccessResponse


class IDEncodeLookupMixin:
    """Use this mixin for Viewsets to use hash ID in url."""

    def get_object(self):
        if "id" in self.kwargs and not str(self.kwargs["id"].isdigit()):
            self.kwargs["id"] = self.kwargs["id"]
        return super(IDEncodeLookupMixin, self).get_object()


class IdDecodeModelViewSet(viewsets.ModelViewSet):
    """Viewset to decode id to normal id."""

    lookup_url_kwarg = "hashid"

    def get_object(self):
        return self.basename.objects.get(id=self.kwargs["hashid"])


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
