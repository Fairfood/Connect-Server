"""URLs of the app supply_chains."""
from django.urls import path
from django.urls import include
from rest_framework import routers

from v1.supply_chains.views import CompanyMemberViewSet
from v1.supply_chains.views import CompanyProductViewSet
from v1.supply_chains.views import CompanyViewSet
from v1.supply_chains.views import EntityCardViewSet
from v1.supply_chains.views import FarmerViewSet
from v1.supply_chains.views import FarmerDetailsAPI
from v1.supply_chains.views import OpenTransactionAPI
from v1.supply_chains.views import OpenTransactionDetails

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

urlpatterns = [
    path("open/farmer/<pk>/", FarmerDetailsAPI.as_view()),
    path("open/transaction/", OpenTransactionAPI.as_view()),
    path("open/transaction/<pk>/",OpenTransactionDetails.as_view()),
    path("", include(router.urls)),

]
