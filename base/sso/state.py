from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from rest_framework_simplejwt.backends import TokenBackend

from .settings import sso_settings


def get_verification_key():
    with open(sso_settings.VERFIFICATION_FILE_PATH, "rb") as key_file:
            key = serialization.load_pem_public_key(
                key_file.read(), backend=default_backend()
            )
    return key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

token_backend = TokenBackend(
    sso_settings.ALGORITHM,
    None,
    get_verification_key(),
    sso_settings.AUDIENCE,
    sso_settings.ISSUER,
    None,
    sso_settings.LEEWAY
)
