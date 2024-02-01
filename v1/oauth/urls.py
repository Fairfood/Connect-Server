from django.urls import re_path
from oauth2_provider import views

urlpatterns = [re_path(r"^token/$", views.TokenView.as_view(), name="token")]
