"""URLs of the app supply_chains."""
from django.urls import include, path
from rest_framework import routers

from v1.supply_chains.views import (CompanyMemberView, CompanyMemberViewSet,
                                    CompanyProductViewSet, CompanyViewSet,
                                    EntityCardViewSet, FarmerDetailsAPI,
                                    FarmerViewSet, OpenTransactionAPI,
                                    OpenTransactionDetails, 
                                    DownloadIncomingTransactionsView, 
                                    FarmerConsentAlertView)

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
    path("open/farmer-consent/alert/", FarmerConsentAlertView.as_view()),
    path(
        'admin/company/<slug:id>/download_transactions/', 
        DownloadIncomingTransactionsView.as_view(), 
        name='download_transactions'
    ),
    path("", include(router.urls)),
    path("company/<pk>/members/",CompanyMemberView.as_view()),

]
