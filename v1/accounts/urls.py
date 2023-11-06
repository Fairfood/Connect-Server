"""URLs of the app accounts."""
from django.urls import path
from rest_framework import routers

from v1.accounts.views import user as user_viewset


router = routers.SimpleRouter()

router.register(r"users", user_viewset.UserViewSet, basename="users")

urlpatterns = router.urls

urlpatterns += [
    path(
        "privacy-policy/",
        user_viewset.PrivacyPolicy.as_view(),
        name="get_privacy_policy",
    ),
]
