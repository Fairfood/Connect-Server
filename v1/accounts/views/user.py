from rest_framework import generics

from base.request_handler.views import IdDecodeModelViewSet
from v1.accounts import models as user_models
from v1.accounts.serializers import user as user_serializers

# from v1.apiauth import permissions as auth_permissions


class UserViewSet(IdDecodeModelViewSet):
    """A simple ViewSet for viewing and editing accounts."""

    queryset = (
        user_models.CustomUser.objects.all()
        .select_related("default_entity")
        .prefetch_related("member_companies")
    )
    serializer_class = user_serializers.UserSerializer
    http_method_names = [
        "get",
        "patch",
    ]


class PrivacyPolicy(generics.RetrieveAPIView):
    """Api to rerive data about latest privacy policy."""

    serializer_class = user_serializers.PrivacyPolicySerializer
    authentication_classes = []
    permission_classes = []

    def get_object(self):
        """Return latest privacy policy which is under effect from today."""
        return user_models.PrivacyPolicy.current_privacy_policy()
