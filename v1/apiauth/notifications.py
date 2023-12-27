"""Notifications in apiauth module."""
from django.utils.translation import gettext_lazy as _

from v1.notifications.constants import NotificationCondition
from v1.notifications.manager import BaseNotificationManager


class PasswordResetNotificationManager(BaseNotificationManager):
    """Notification for sending email notification for re-setting password.

    This manager handles the notification for password reset actions,
    specifically sending email notifications.
    """

    notification_uid: str = "password_reset"
    action_text: str = _("Change Password")
    url_path: str = "reset"

    visibility: dict = {"__all__": NotificationCondition.DISABLED}
    push: dict = {"__all__": NotificationCondition.DISABLED}
    email: dict = {"__all__": NotificationCondition.ENABLED}
    sms: dict = {"__all__": NotificationCondition.DISABLED}

    email_template: str = "reset_password.html"

    def get_title(self) -> str:
        """Get the title for the password reset email notification.

        Returns:
            str: The title for the email notification.
        """
        return _(
            "Received password reset request for your trace_connect Account"
        )

    def get_body(self) -> str:
        """Get the body for the password reset email notification.

        Returns:
            str: The body for the email notification.
        """
        return _(
            "Received password reset request for your trace_connect Account"
        )

    def get_url_params(self) -> dict:
        """Get the URL parameters for the password reset email notification.

        Returns:
            dict: URL parameters including token, salt, and user_id.
        """
        return {
            "token": self.action_object.key,
            "salt": self.action_object.id,
            "user_id": self.user.id,
        }

    def get_actor_entity(self):
        """Get the actor entity for the notification.

        Returns:
            None: Since this notification doesn't involve a specific actor
            entity.
        """
        return None

    def get_target_entity(self):
        """Get the target entity for the notification.

        Returns:
            None: Since this notification doesn't involve a specific target
            entity.
        """
        return None
