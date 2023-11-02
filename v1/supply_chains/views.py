from .filters import EntityCardFilterSet
from .filters import FarmerFilterSet
from base.request_handler.views import IdDecodeModelViewSet
from v1.supply_chains.models.base_models import EntityCard
from v1.supply_chains.models.company_models import Company
from v1.supply_chains.models.farmer_models import Farmer
from v1.supply_chains.serializers import CompanySerializer
from v1.supply_chains.serializers import EntityCardSerializer
from v1.supply_chains.serializers import FarmerSerializer


class EntityCardViewSet(IdDecodeModelViewSet):
    """
    A viewset for viewing and editing EntityCard instances.
    """

    queryset = EntityCard.objects.all()
    serializer_class = EntityCardSerializer
    http_method_names = ("get", "post")
    filterset_class = EntityCardFilterSet


class CompanyViewSet(IdDecodeModelViewSet):
    """
    A viewset for viewing and editing Company instances.
    """

    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    http_method_names = ("get",)


class FarmerViewSet(IdDecodeModelViewSet):
    """
    A viewset for viewing and editing Farmer instances.
    """

    queryset = Farmer.objects.all()
    serializer_class = FarmerSerializer
    http_method_names = (
        "get",
        "post",
        "put",
    )
    filterset_class = FarmerFilterSet
