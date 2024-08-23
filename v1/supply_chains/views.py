from django.db.models import Q
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from base.exceptions.custom_exceptions import BadRequest
from base.request_handler.views import IDDEcodeScopeViewset
from utilities.functions import decode
from v1.supply_chains.models.base_models import EntityCard
from v1.supply_chains.models.company_models import (Company, CompanyMember,
                                                    CompanyProduct)
from v1.supply_chains.models.farmer_models import Farmer
from v1.supply_chains.serializers import (AppFarmerSerializer,
                                          CompanyCreateSerializer,
                                          CompanyMemerSerializer,
                                          CompanyProductSerializer,
                                          CompanySerializer,
                                          EntityCardSerializer,
                                          FarmerSerializer,
                                          OpenTransactionSerializer)
from v1.transactions.models.transaction_models import ProductTransaction

from .filters import (EntityCardFilterSet, FarmerFilterSet,
                      OpenFilterTransactions)


class EntityCardViewSet(IDDEcodeScopeViewset):
    """A viewset for viewing and editing EntityCard instances."""

    queryset = EntityCard.objects.all()
    serializer_class = EntityCardSerializer
    http_method_names = ("get", "post")
    resource_types = ["company", "farmer"]
    filterset_class = EntityCardFilterSet


class CompanyViewSet(IDDEcodeScopeViewset):
    """A viewset for viewing and editing Company instances.

    This viewset extends the IdDecodeModelViewSet and provides
    customization for viewing and editing Company instances in the API.
    """

    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    http_method_names = (
        "get",
        "post",
        "patch",
    )
    resource_types = ["company"]

    def get_serializer_class(self):
        """Get the serializer class based on the action.

        Returns the CompanyCreateSerializer for create, update,
        and partial_update actions, and the default CompanySerializer for
        other actions.

        Returns:
            Serializer: The appropriate serializer class based on the action.
        """
        if self.action in ["create", "update", "partial_update"]:
            return CompanyCreateSerializer
        return super().get_serializer_class()


class FarmerViewSet(IDDEcodeScopeViewset):
    """A viewset for viewing and editing Farmer instances."""

    queryset = Farmer.objects.all()
    serializer_class = FarmerSerializer
    http_method_names = (
        "get",
        "post",
        "patch",
    )
    resource_types = ["farmer"]
    filterset_class = FarmerFilterSet

    @action(methods=("post",), detail=False, url_path="bulk-create")
    def bulk_create(self, request):
        "bulk create"
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(["Created"], status=status.HTTP_201_CREATED)


class CompanyMemberViewSet(IDDEcodeScopeViewset):
    """A viewset for viewing and editing CompanyMember instances."""

    queryset = CompanyMember.objects.all()
    serializer_class = CompanyMemerSerializer
    resource_types = ["company"]
    http_method_names = ("post",)


class CompanyProductViewSet(IDDEcodeScopeViewset):
    """A viewset for viewing and editing CompanyProduct instances."""

    queryset = CompanyProduct.objects.all()
    serializer_class = CompanyProductSerializer
    resource_types = ["company"]
    http_method_names = ("post",)


class FarmerDetailsAPI(generics.ListAPIView):
    """API to get app Farmer details."""

    serializer_class = AppFarmerSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        # """To perform function get_queryset."""
        try:
            fair_id = (
                str(self.kwargs["pk"]).upper().lstrip("FF").replace(" ", "")
            )
            entity = EntityCard.objects.filter(
                card__display_id__iexact=fair_id).order_by('-created_on').first().entity
        except Exception:
            raise BadRequest("Invalid card number")
        if not Farmer.objects.filter(id=entity.id).exists():
            raise BadRequest("No farmer associated with this card number.")

        return  Farmer.objects.filter(id=entity.id)


class OpenTransactionAPI(generics.ListAPIView):
    """View for list transaction details of particular farmer.

    The farmer id is passing through params.
    """

    serializer_class = OpenTransactionSerializer
    permission_classes = (AllowAny,)
    filterset_class = OpenFilterTransactions

    def get_queryset(self):
        """To perform function get_queryset."""
        card_id = self.request.query_params.get("card_id", None)
        fair_id = card_id.upper().lstrip("FF").replace(" ", "")
        entity_card = EntityCard.objects.filter(card__display_id__iexact=fair_id).order_by('-created_on').first()
        if not entity_card:
            raise BadRequest("Invalid card number")
        if not entity_card.entity:
            raise BadRequest("Invalid card number")
        entity = entity_card.entity
        query = Q(source__id=entity.id) | Q(destination__id=entity.id)
        return ProductTransaction.objects.filter(query).order_by("-date")
        
    
class OpenTransactionDetails(generics.ListAPIView):
    """View for transaction details."""

    serializer_class = OpenTransactionSerializer
    permission_classes = (AllowAny,)


    def get(self, request, *args, **kwargs):
        """function for get the details of transaction.


        and here transaction id in encrypted format. so decrypt id
        before filter Transaction.
        """
        trans_id = kwargs["pk"]
        try:
            transaction = ProductTransaction.objects.get(
                id=decode(trans_id))
        except Exception:
            raise BadRequest("Invalid Transaction id.")

        serializer = OpenTransactionSerializer(
            transaction, data=request.data, partial=True, context=self.kwargs
        )
        if not serializer.is_valid():
            raise BadRequest(serializer.errors)
        return Response(serializer.data)
