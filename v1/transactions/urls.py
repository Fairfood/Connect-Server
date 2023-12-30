"""URLs of the app supply_chains."""
from rest_framework import routers

from .views import PaymentTransactionViewSet
from .views import ProductTransactionViewSet

router = routers.DefaultRouter()
router.register(
    "product-transactions",
    ProductTransactionViewSet,
    basename="product-transactions",
)

router.register(
    "payment-transactions",
    PaymentTransactionViewSet,
    basename="payment-transactions",
)

urlpatterns = router.urls
