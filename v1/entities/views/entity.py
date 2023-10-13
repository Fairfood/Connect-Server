from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import generics
from rest_framework.views import APIView

from base import exceptions as base_exceptions
from base.authentication import utilities as auth_utils
from base.request_handler.response import SuccessResponse
from base.request_handler.views import IdDecodeModelViewSet
from v1.accounts import constants as user_consts
from v1.entities import constants as entity_consts
from v1.entities import filters as entity_filters
from v1.entities import models as entity_models
from v1.entities.serializers import entity as entity_serializers

# from v1.apiauth import permissions as auth_permissions


class EntityRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """"""

    serializer_class = entity_serializers.EntitySerializer

    def get_queryset(self):
        """"""
        if self.request.method == "PATCH":
            current_entity = auth_utils.get_current_entity()
            query = Q(
                status=entity_consts.EntityStatus.INACTIVE,
                invited_by=current_entity,
            )
            query |= Q(id=current_entity.id)
            return entity_models.Entity.objects.filter(query)
        return entity_models.Entity.objects.all().select_related(
            "operation", "province"
        )


class EntityDocumentViewSet(IdDecodeModelViewSet):
    """"""

    serializer_class = entity_serializers.EntityDocumentSerializer
    http_method_names = [
        "get",
        "post",
        "patch",
        "delete",
    ]

    def get_queryset(self):
        """"""
        entity = auth_utils.get_current_entity()
        companies = (
            entity_models.EntityDocument.objects.filter(
                entity=entity, is_deleted=False
            )
            .select_related("entity", "category")
            .order_by("-created_on")
        )
        return companies

    def destroy(self, request, *args, **kwargs):
        """Destroy overrided to check entity of the user and document are
        same."""
        entity = auth_utils.get_current_entity()
        document = self.get_object()
        if document.entity != entity:
            raise base_exceptions.BadRequest(_("Document can not be deleted."))
        document.delete()
        return SuccessResponse(_("Document deleted successfully."))


class EntityMemberViewSet(IdDecodeModelViewSet):
    """"""

    filterset_class = entity_filters.EntityMemberFilter
    serializer_class = entity_serializers.EntityMemberSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["user__first_name", "user__last_name"]
    http_method_names = [
        "get",
        "post",
        "patch",
        "delete",
    ]

    def get_queryset(self):
        """"""
        entity = auth_utils.get_current_entity()
        members = (
            entity_models.EntityMember.objects.filter(
                entity=entity, is_active=True
            )
            .select_related("user")
            .order_by("-created_on")
        )
        return members

    def destroy(self, request, *args, **kwargs):
        """Destroy overrided to delete entity member and to remove the default
        entity of the user if the default entity is the entity member's
        entity."""
        entity = auth_utils.get_current_entity()
        member = self.get_object()
        if member.type == entity_consts.EntityMemberType.SUPER_ADMIN:
            raise base_exceptions.BadRequest(
                _("Can not remove super admin admin.")
            )
        if member.user.default_entity == entity:
            member.user.default_entity = None
            member.user.save()
        member.delete()
        return SuccessResponse(_("Member deleted successfully."))


class ResendEntityMemberInvite(APIView):
    """Resend invite to entity member."""

    def post(self, request, *args, **kwargs):
        """Post overrided to resend invite to a entity member."""
        try:
            entity_member = entity_models.EntityMember.objects.get(
                id=self.request.data.get("id", None),
                entity=auth_utils.get_current_entity(),
                user__status=user_consts.UserStatus.CREATED,
            )
        except entity_models.EntityMember.DoesNotExist:
            raise base_exceptions.BadRequest(_("Entity member does not exist"))
        entity_member.send_invite()
        return SuccessResponse(_("Resend successfully"))
