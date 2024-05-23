from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import EntityCardFilterSet
from .filters import FarmerFilterSet
from base.request_handler.views import IDDEcodeScopeViewset
from v1.supply_chains.models.base_models import EntityCard
from v1.supply_chains.models.company_models import Company
from v1.supply_chains.models.company_models import CompanyMember
from v1.supply_chains.models.company_models import CompanyProduct
from v1.supply_chains.models.farmer_models import Farmer
from v1.supply_chains.serializers import CompanyCreateSerializer
from v1.supply_chains.serializers import CompanyMemerSerializer
from v1.supply_chains.serializers import CompanyProductSerializer
from v1.supply_chains.serializers import CompanySerializer
from v1.supply_chains.serializers import EntityCardSerializer
from v1.supply_chains.serializers import FarmerSerializer


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
