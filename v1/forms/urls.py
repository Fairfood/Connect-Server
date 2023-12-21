"""URLs of the app supply_chains."""
from rest_framework import routers

from v1.forms.views import FormViewSet


router = routers.DefaultRouter()
router.register("forms", FormViewSet, basename="forms")

urlpatterns = router.urls
