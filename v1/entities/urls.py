"""URLs of the app accounts."""

from rest_framework import routers

from django.urls import path

from v1.entities.views import entity as entity_viewset
from v1.entities import models as entity_models


router = routers.SimpleRouter()

urlpatterns = [
    path('members:resend-invite', entity_viewset.ResendEntityMemberInvite.as_view()),
    path('<hashid:pk>/', entity_viewset.EntityRetrieveUpdateView.as_view(),
    name='retrieve-update-company'),
]

router.register(r'documents', entity_viewset.EntityDocumentViewSet,
    basename=entity_models.EntityDocument)
router.register(r'members', entity_viewset.EntityMemberViewSet, 
    basename=entity_models.EntityMember)

urlpatterns += router.urls
