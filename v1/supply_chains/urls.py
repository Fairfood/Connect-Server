"""URLs of the app supply_chains."""
from rest_framework import routers

from v1.supply_chains.views import CompanyMemberViewSet
from v1.supply_chains.views import CompanyProductViewSet
from v1.supply_chains.views import CompanyViewSet
from v1.supply_chains.views import EntityCardViewSet
from v1.supply_chains.views import FarmerViewSet


router = routers.DefaultRouter()
router.register("entity-cards", EntityCardViewSet, basename="entity-cards")
router.register("companies", CompanyViewSet, basename="companies")
router.register("farmers", FarmerViewSet, basename="farmers")
router.register(
    "company-members", CompanyMemberViewSet, basename="company-members"
)
router.register(
    "company-products", CompanyProductViewSet, basename="company-products"
)

urlpatterns = router.urls
