from django.contrib.auth import get_user_model
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from oauth2_provider.models import AbstractAccessToken
from oauth2_provider.models import AbstractApplication
from oauth2_provider.models import redirect_to_uri_allowed

from ..supply_chains.models.company_models import CompanyMember
from v1.supply_chains.constants import CompanyMemberType

UserModel = get_user_model()

# Create your models here.


class ClientServer(AbstractApplication):
    """
    Client Server Model
    """

    user = models.ForeignKey(
        UserModel,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("User"),
    )
    companies = models.ManyToManyField(
        "supply_chains.Company", verbose_name=_("Companies")
    )
    allowed_hosts = models.TextField(
        blank=True,
        help_text=_("Allowed Host list, space separated"),
    )

    def redirect_uri_allowed(self, uri):
        """
        Checks if given url is one of the items in :attr:`allowed_hosts` string

        :param uri: Url to check
        """
        return redirect_to_uri_allowed(uri, self.redirect_uris.split())


class ClientAccessToken(AbstractAccessToken):
    company = models.ForeignKey(
        "supply_chains.Company",
        on_delete=models.CASCADE,
        verbose_name=_("Company"),
    )

    def save(self, *args, **kwargs):
        if not self.pk and not self.user:
            self.user = self.application.user
        super().save(*args, **kwargs)

    def is_valid(self, scopes=None):
        return super().is_valid(scopes) and self.company_allowed()

    def company_allowed(self):
        return self.company in self.application.companies.all()


@receiver(models.signals.post_save, sender=ClientServer)
def create_client_user(sender, instance, created, **kwargs):
    if created:
        for company in instance.companies.all():
            obj, _ = CompanyMember.objects.get_or_create(
                company=company, user=instance.user
            )
            obj.type = CompanyMemberType.ADMIN
            obj.save()
