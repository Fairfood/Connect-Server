"""URLs of the app accounts."""

from rest_framework import routers

from django.urls import path

from v1.accounts.views import user as user_viewset

from v1.accounts import models as user_models


router = routers.SimpleRouter()

router.register(r'users', user_viewset.UserViewSet, 
    basename=user_models.CustomUser)

urlpatterns = router.urls

urlpatterns += [
    path('privacy-policy/', user_viewset.PrivacyPolicy.as_view(), 
    name='get_privacy_policy'),
    ]
