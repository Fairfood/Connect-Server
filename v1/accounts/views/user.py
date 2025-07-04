from rest_framework import generics
from rest_framework.response import Response

from base.request_handler.views import IDDEcodeScopeViewset
from v1.accounts import models as user_models
from v1.accounts.filters import UserFilter
from v1.accounts.serializers import user as user_serializers

# from v1.apiauth import permissions as auth_permissions


class UserViewSet(IDDEcodeScopeViewset):
    """A simple ViewSet for viewing and editing accounts."""

    queryset = (
        user_models.CustomUser.objects.all()
        .select_related("default_entity")
        .prefetch_related("member_companies")
    )
    resource_types = ["user"]
    serializer_class = user_serializers.UserSerializer
    http_method_names = [
        "get",
        "patch",
        "post",
    ]
    filterset_class = UserFilter



class PrivacyPolicy(generics.RetrieveAPIView):
    """Api to rerive data about latest privacy policy."""

    serializer_class = user_serializers.PrivacyPolicySerializer
    authentication_classes = []
    permission_classes = []

    def get_object(self):
        """Return latest privacy policy which is under effect from today."""
        return user_models.PrivacyPolicy.current_privacy_policy()


# class UserDetailsView(generics.GenericAPIView):
#     queryset = user_models.CustomUser.objects.all()
#     serializer_class = user_serializers.UserSerializer
#     http_method_names = ["get"]

#     def get_object(self):
#         queryset = self.filter_queryset(self.get_queryset())
#         filter_kwargs = {self.lookup_field: self.request.user.pk}
#         obj = generics.get_object_or_404(queryset, **filter_kwargs)

#         # May raise a permission denied
#         self.check_object_permissions(self.request, obj)
#         return obj

#     def get(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance)
#         return Response(serializer.data)