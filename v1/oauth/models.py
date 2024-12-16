from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from oauth2_provider.models import (AbstractAccessToken, AbstractApplication,
                                    AbstractIDToken, AbstractRefreshToken,
                                    redirect_to_uri_allowed)

from v1.supply_chains.constants import CompanyMemberType

from ..supply_chains.models.company_models import CompanyMember

UserModel = get_user_model()

# Create your models here.


class ClientServer(AbstractApplication):
    """Client Server Model."""

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
        """Checks if given url is one of the items in :attr:`allowed_hosts`
        string.

        :param uri: Url to check
        """
        return redirect_to_uri_allowed(uri, self.redirect_uris.split())


class ClientAccessToken(AbstractAccessToken):
    """Custom Access Token model for OAuth2 clients associated with companies.

    This class extends the AbstractAccessToken provided by Django OAuth
    Toolkit and includes additional fields and methods related to company
    association.

    Attributes:
        company (ForeignKey): A foreign key relationship to the "Company"
            model.

    Methods:
        save(*args, **kwargs): Overrides the save method to set the user
            based on the associated application's user if not provided.
        is_valid(scopes=None): Overrides the is_valid method to check if
            the token is valid and the associated company is allowed.
        allow_scopes(scopes): Overrides the allow_scopes method to check
            if the specified scopes are allowed.
        company_allowed(): Checks if the associated company is allowed
            based on the associated application's companies.
    """

    company = models.ForeignKey(
        "supply_chains.Company",
        on_delete=models.CASCADE,
        verbose_name=_("Company"),
    )

    def save(self, *args, **kwargs):
        """Overrides the save method to set the user based on the associated
        application's user if not provided.

        Args:
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        if not self.pk and not self.user:
            self.user = self.application.user
        super().save(*args, **kwargs)

    def is_valid(self, scopes=None):
        """Overrides the is_valid method to check if the token is valid and the
        associated company is allowed.

        Args:
            scopes (list): List of requested scopes.

        Returns:
            bool: True if the token is valid and the associated company is
                  allowed, False otherwise.
        """
        return super().is_valid(scopes) and self.company_allowed()

    def allow_scopes(self, scopes):
        """Overrides the allow_scopes method to check if the specified scopes
        are allowed.

        Args:
            scopes (list): List of requested scopes.

        Returns:
            bool: True if the specified scopes are allowed, False otherwise.
        """
        if not scopes:
            return False
        if (
            len(scopes) == 1
            and scopes[0] == settings.OAUTH2_PROVIDER_AUTH_SCOPE
        ):
            return True
        return super().allow_scopes(scopes)

    def company_allowed(self):
        """Checks if the associated company is allowed based on the associated
        application's companies.

        Returns:
            bool: True if the associated company is allowed, False otherwise.
        """
        return self.company in self.application.companies.all()


class ClientServerCompany(models.Model):
    """Client Server Company Model.

    Represents the association between a Client Server and a Company. When
    a Client Server is associated with a Company, a corresponding
    CompanyMember is created with the Client Server as an admin.

    Attributes:
        client_server (ForeignKey): A foreign key relationship to the
            "ClientServer" model.
        company (ForeignKey): A foreign key relationship to the "Company"
            model.

    Methods:
        save(*args, **kwargs): Overrides the save method to create a
            CompanyMember with the associated Client Server as an admin.
        create_client_user(): Creates a CompanyMember with the associated
            Client Server as an admin.

    Meta:
        unique_together (tuple): Specifies that the combination of
            client_server and company should be unique.
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
        """Overrides the save method to create a CompanyMember with the
        associated Client Server as an admin.

        Args:
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.create_client_user()
        super().save(*args, **kwargs)

    def create_client_user(self):
        """Creates a CompanyMember with the associated Client Server as an
        admin.

        Returns:
            None
        """
        obj, created = CompanyMember.objects.get_or_create(
            company=self.company, user=self.client_server.user
        )
        obj.type = CompanyMemberType.ADMIN
        obj.save()


class ClientIDToken(AbstractIDToken):
    """Custom ID Token model for OAuth2 clients.

    This class extends the AbstractIDToken provided by Django OAuth Toolkit
    and can be swapped with the model specified in the settings.

    Meta:
        swappable (str): Specifies the model to be swapped with.

    Attributes:
        None
    """

    class Meta:
        swappable = "OAUTH2_PROVIDER_ID_TOKEN_MODEL"


class ClientRefreshToken(AbstractRefreshToken):
    """Custom Refresh Token model for OAuth2 clients.

    This class extends the AbstractRefreshToken provided by Django OAuth
    Toolkit and can be swapped with the model specified in the settings.

    Meta:
        swappable (str): Specifies the model to be swapped with.

    Attributes:
        None
    """

    class Meta:
        swappable = "OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL"
