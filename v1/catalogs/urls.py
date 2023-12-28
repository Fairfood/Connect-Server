"""URLs of the app catalogs."""
from rest_framework import routers

from .views import products as product_views
from v1.catalogs.views import currency as currency_views

router = routers.SimpleRouter()

router.register(
    r"currencies",
    currency_views.CurrencyViewSet,
    basename="currencies",
)
router.register(r"products", product_views.ProductViewSet, basename="products")
router.register(r"premiums", product_views.PremiumViewSet, basename="premiums")
router.register(
    r"connect-cards",
    product_views.ConnectCardViewSet,
    basename="connect-cards",
)

urlpatterns = router.urls

urlpatterns += [
    # Authentication APIS
]
