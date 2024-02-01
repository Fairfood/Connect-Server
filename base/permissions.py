from rest_framework import permissions
from rest_framework_simplejwt.settings import api_settings as jwt_settings


class CombinedPermission(permissions.BasePermission):
    """
    This permission class checks the type of authentication token in the
    request and delegates permission checks to the appropriate permission class
    based on the token type.

    Methods:
        has_permission(request, view): Check if the user has permission to
            access the view.
        has_object_permission(request, view, obj): Check if the user has
            permission to perform the action on the object.
    """

    def has_permission(self, request, view):
        """
        Check if the user has permission to access the view.

        Args:
            request (HttpRequest): The HTTP request being checked for
                permission.
            view (View): The Django REST framework view being accessed.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        permission = self.permission(request)
        return permission.has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to perform the action on the object.

        Args:
            request (HttpRequest): The HTTP request being checked for
                permission.
            view (View): The Django REST framework view being accessed.
            obj (object): The object being acted upon.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        permission = self.permission(request)
        return permission.has_object_permission(request, view, obj)

    def permission(self, request):
        """
        Get the appropriate permission class based on the authentication token
        type.

        Args:
            request (HttpRequest): The HTTP request being checked for
                permission.
        """
        token = request.auth
        if not token:
            return False

        if token.__class__ in jwt_settings.AUTH_TOKEN_CLASSES:
            return permissions.IsAuthenticated()
        else:
            from oauth2_provider.contrib.rest_framework import (
                TokenMatchesOASRequirements,
            )

            return TokenMatchesOASRequirements()
