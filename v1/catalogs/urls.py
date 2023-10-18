"""URLs of the app catalogs."""
from rest_framework import routers

from v1.catalogs.models import common_models as catalog_models
from v1.catalogs.views import category as category_views
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
    r"region", country_views.RegionViewSet, basename=catalog_models.Region
)
router.register(
    r"villages", country_views.VillageViewSet, basename=catalog_models.Village
)
router.register(
    r"currencies",
    currency_views.CurrencyViewSet,
    basename=catalog_models.Currency,
)
router.register(
    r"categories",
    category_views.CategoryViewSet,
    basename=catalog_models.Category,
)
urlpatterns = router.urls

urlpatterns += [
    # Authentication APIS
]
