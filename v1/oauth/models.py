from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
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
        settings.AUTH_USER_MODEL,
        related_name="%(app_label)s_%(class)s",
        on_delete=models.PROTECT,
    )
    companies = models.ManyToManyField(
        "supply_chains.Company",
        through="oauth.ClientServerCompany",
        through_fields=("client_server", "company"),
        verbose_name=_("Companies"),
    )
    scope = models.TextField(
        blank=True,
        help_text=_("Scope required by this application, space separated"),
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

    def allow_scopes(self, scopes):
        if not scopes:
            return False
        if (
            len(scopes) == 1
            and scopes[0] == settings.OAUTH2_PROVIDER_AUTH_SCOPE
        ):
            return True
        return super().allow_scopes(scopes)

    def company_allowed(self):
        return self.company in self.application.companies.all()


class ClientServerCompany(models.Model):
    """
    Client Server Company Model
    """

    client_server = models.ForeignKey(
        ClientServer,
        on_delete=models.CASCADE,
        verbose_name=_("Client Server"),
    )
    company = models.ForeignKey(
        "supply_chains.Company",
        on_delete=models.CASCADE,
        verbose_name=_("Company"),
    )

    class Meta:
        unique_together = ("client_server", "company")

    def save(self, *args, **kwargs):
        self.create_client_user()
        super().save(*args, **kwargs)

    def create_client_user(self):
        obj, _ = CompanyMember.objects.get_or_create(
            company=self.company, user=self.client_server.user
        )
        obj.type = CompanyMemberType.ADMIN
        obj.save()
