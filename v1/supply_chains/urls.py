"""URLs of the app supply_chains."""
from rest_framework import routers

from v1.supply_chains.views import CompanyViewSet
from v1.supply_chains.views import EntityCardViewSet


router = routers.DefaultRouter()
router.register("entity-cards", EntityCardViewSet, basename="entity-cards")
router.register("companies", CompanyViewSet, basename="companies")
router.register("farmers", CompanyViewSet, basename="farmers")

urlpatterns = router.urls
