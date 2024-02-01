from oauth2_provider.exceptions import InvalidRequestFatalError
from oauth2_provider.oauth2_validators import AccessToken
from oauth2_provider.oauth2_validators import OAuth2Validator
from oauth2_provider.scopes import get_scopes_backend
from oauthlib.oauth2.rfc6749 import utils

from v1.supply_chains.models.company_models import CompanyMember


class OAuth2ClientAccessValidator(OAuth2Validator):
    """
    Custom OAuth 2.0 access token validator for client applications.

    This validator extends the default OAuth2Validator and provides additional
    functionality for creating access tokens and retrieving default scopes.

    Attributes:
        None

    Methods:
        is_valid_entity: Validate the entity ID in the request.
        _create_access_token: Create and return an AccessToken instance.
        get_default_scopes: Retrieve the default scopes for a given client and
            request.
    """

    def is_valid_entity(self, entity_id, request):
        """
        Validate the entity ID in the request.

        Args:
            entity_id (str): The entity ID in the request.
            request (oauthlib.common.Request): The request object.

        Returns:
            bool: True if the entity ID is valid, False otherwise.
        """
        try:
            member = CompanyMember.objects.get(
                user_id=request.client.user_id, company_id=entity_id
            )
            return member.is_active
        except CompanyMember.DoesNotExist:
            return False

    def _create_access_token(
        self, expires, request, token, source_refresh_token=None
    ):
        """
        Create and return an AccessToken instance.

        Args:
            expires (datetime): The expiration datetime of the access token.
            request (oauthlib.common.Request): The request object.
            token (dict): The token data containing 'access_token', 'id_token',
                etc.
            source_refresh_token (oauth2_provider.models.RefreshToken, optional
            ):
                The refresh token from which the access token is generated.

        Returns:
            oauth2_provider.models.AccessToken: The created AccessToken
                instance.
        """

        entity_id = request.headers.get("HTTP_X_ENTITY_ID", None)
        if not self.is_valid_entity(entity_id, request):
            raise InvalidRequestFatalError(
                "Invalid entity ID. Or entity is not active."
            )
        id_token = token.get("id_token", None)
        if id_token:
            id_token = self._load_id_token(id_token)
        return AccessToken.objects.create(
            user=request.client.user,
            scope=token["scope"],
            expires=expires,
            token=token["access_token"],
            id_token=id_token,
            application=request.client,
            source_refresh_token=source_refresh_token,
            company_id=entity_id,
        )

    def get_default_scopes(self, client_id, request, *args, **kwargs):
        """
        Retrieve the default scopes for the given client and request.

        Args:
            client_id (str): The client identifier.
            request (oauthlib.common.Request): The request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            list: A list of default scopes for the client and request.
        """
        default_scopes_from_backend = get_scopes_backend().get_default_scopes(
            application=request.client, request=request
        )
        application_scope = utils.scope_to_list(request.client.scope)
        default_scopes = list(
            set(default_scopes_from_backend) & set(application_scope)
        )
        return default_scopes or default_scopes_from_backend
