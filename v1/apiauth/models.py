import uuid
from datetime import datetime

from django.db import models

from base.db.models import AbstractBaseModel


class AuthSession(AbstractBaseModel):
    """
    Model to store the session token, client_nonce, and server_nonce for each session.
    """

    session_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    client_nonce = models.CharField(max_length=256, unique=True)
    server_nonce = models.UUIDField(default=uuid.uuid4, editable=False)
    device_id = models.CharField(max_length=256, null=True, blank=True)  # To track device
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, default=None, blank=True)

    def is_valid(self):
        """
        Check if the session token is still valid by comparing the expiration time.
        """
        return datetime.now() < self.expires_at

    def __str__(self):
        return f"Session {self.session_token} (Valid until {self.expires_at})"

    def validate_session_token(session_token, client_nonce):
        """
        Validate that the session token is valid and matches the provided client_nonce.

        Args:
            session_token (UUID): The session token to validate.
            client_nonce (str): The client's nonce to compare with the server-stored one.

        Returns:
            bool: True if the session is valid, otherwise False.
        """
        try:
            session = AuthSession.objects.get(session_token=session_token)

            # Check if the session has expired
            if not session.is_valid():
                return False

            # Check if the client_nonce matches the stored one
            if session.client_nonce != client_nonce:
                return False

            return True
        except AuthSession.DoesNotExist:
            return False
