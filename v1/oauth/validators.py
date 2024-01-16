from oauth2_provider.oauth2_validators import AccessToken
from oauth2_provider.oauth2_validators import OAuth2Validator


class OAuth2ClientAccessValidator(OAuth2Validator):
    def _create_access_token(
        self, expires, request, token, source_refresh_token=None
    ):
        id_token = token.get("id_token", None)
        if id_token:
            id_token = self._load_id_token(id_token)
        return AccessToken.objects.create(
            user=request.user,
            scope=token["scope"],
            expires=expires,
            token=token["access_token"],
            id_token=id_token,
            application=request.client,
            source_refresh_token=source_refresh_token,
            company=request.entity,
        )
