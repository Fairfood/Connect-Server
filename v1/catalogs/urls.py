"""URLs of the app catalogs."""
from rest_framework import routers

from .views import products as product_views
from v1.catalogs.models import common_models as catalog_models
from v1.catalogs.views import country as country_views
from v1.catalogs.views import currency as currency_views

router = routers.SimpleRouter()

router.register(
    r"countries", country_views.CountryViewSet, basename=catalog_models.Country
)
router.register(
    r"provinces",
    country_views.ProvinceViewSet,
    basename=catalog_models.Province,
)
router.register(
    r"currencies",
    currency_views.CurrencyViewSet,
    basename=catalog_models.Currency,
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
