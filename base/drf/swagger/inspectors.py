from drf_yasg import openapi
from drf_yasg.inspectors import FieldInspector
from drf_yasg.inspectors import NotHandled
from rest_framework.relations import PrimaryKeyRelatedField

from base.drf.fields import SerializableRelatedField


class HashidFieldInspector(FieldInspector):
    """Custom field inspector for Hashid fields."""

    def field_to_swagger_object(
        self, field, swagger_object_type, use_references, **kwargs
    ):
        """Convert field to swagger object."""
        if isinstance(field, PrimaryKeyRelatedField):
            # Define the field as a string in Swagger
            return openapi.Schema(type=openapi.TYPE_STRING)
        if isinstance(field, SerializableRelatedField):
            # Define the field as a string in Swagger
            return openapi.Schema(type=openapi.TYPE_STRING)
        return NotHandled
