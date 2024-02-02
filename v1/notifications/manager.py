from django.conf import settings
from django.utils.translation import gettext_lazy as _

from utilities.translations import internationalize_attribute
from v1.notifications.constants import NotificationCondition
from v1.notifications.models import Notification

NOTIFICATION_TYPES = {}


class BaseNotificationManager:
    """Base class to use for notifications.

    Notifications should be defined in the corresponding apps after
    inheriting from this base class.
    """

    notification_uid: str = ""

    action_text: str = _("Dashboard")
    url_path: str = "/notifications/"

    visibility: dict = {"__all__": NotificationCondition.ENABLED}
    push: dict = {"__all__": NotificationCondition.IF_USER_ACTIVE}
    email: dict = {"__all__": NotificationCondition.IF_USER_ACTIVE}
    sms: dict = {"__all__": NotificationCondition.DISABLED}

    email_template: str = "default.html"

    def __init__(self, user, action_object, token=None, context=None):
        """Initialize notification.

        Args:
            user: User object for whom the notification is created.
            action_object: The object associated with the notification.
            token: Validation token for the notification.
            context: Additional context for the notification.
        """
        from v1.supply_chains.models.company_models import CompanyMember

        # curr_language = translation.get_language()
        context = context or {}
        self.user = user
        self.action_object = action_object
        target_entity = self.get_target_entity()
        member = CompanyMember.objects.filter(
            company=target_entity, user=user
        ).first()
        notif_prefs = (
            member.get_notification_pref(self)
            if member
            else user.get_notification_pref(self)
        )
        if any(notif_prefs.values()):

            # action_object_class = action_object.__class__
            notification, created = Notification.objects.get_or_create(
                user=user,
                type=self.notification_uid,
                visibility=notif_prefs["visibility"],
                action_push=notif_prefs["push"],
                action_email=notif_prefs["email"],
                action_sms=notif_prefs["sms"],
                event_id=action_object.id,
                validation_token=token,
            )
            self.notification_object = notification

            internationalize_attribute(notification, "title", self.get_title)
            internationalize_attribute(notification, "body", self.get_body)

            notification.action_url = self.get_action_url()
            notification.actor_entity = self.get_actor_entity()
            notification.target_entity = self.get_target_entity()
            notification.send_to = self.get_send_to()
            notification.context = context
            notification.event = action_object
            notification.redirect_id = self.get_redirect_id()
            notification.redirect_type = self.get_redirect_type()
            notification.save()
            self.notification_object = notification

    def send_notification(self):
        """Send the notification."""
        # if not self.notification_object:
        #     return False
        # return self.notification_object.send()
        pass

    def get_action_url(self) -> str:
        """Get the action URL for the notification."""
        try:
            url = settings.FRONT_ROOT_URL + self.get_url_path()
            params = self.get_url_params()
            params["notification_id"] = self.notification_object.id
            params["user"] = self.user.id
            params["language"] = self.user.language
            if self.notification_object.validation_token:
                params["token"] = self.notification_object.validation_token.key
                params["salt"] = self.notification_object.validation_token.id
            url.add_params(**params)
            return url
        except TypeError:
            return ""

    def get_title(self) -> str:
        """Get the title for the notification."""
        return (
            f"Notification for {self.user.username} for {self.action_object}."
        )

    def get_body(self) -> str:
        """Get the body for the notification."""
        return (
            f"Notification for {self.user.username} for {self.action_object}."
        )

    def get_url_path(self):
        """Get the URL path for the notification."""
        return self.url_path

    def get_url_params(self) -> dict:
        """Get additional URL parameters for the notification."""
        return {}

    def get_send_to(self) -> str:
        """Get the recipient for the notification."""
        return self.user.email

    def get_actor_entity(self):
        """Get the actor entity associated with the notification."""
        raise NotImplementedError()

    def get_target_entity(self):
        """Get the target entity associated with the notification."""
        raise NotImplementedError()

    def get_redirect_id(self):
        """Get the redirect ID for the notification."""
        return None

    def get_redirect_type(self):
        """Get the redirect type for the notification."""
        return ""


def validate_notifications():
    """Validate notification preferences for all notification types.

    This function iterates through all subclasses of
    BaseNotificationManager and checks the validity of their
    notification preferences. It ensures that preferences are defined
    appropriately and that the notification_uid is unique.
    """

    from v1.supply_chains.constants import CompanyMemberType

    def check_pref(pref: dict) -> bool:
        pref_keys = pref.keys()
        if "__all__" in pref_keys:
            if len(pref_keys) == 1:
                return True
            raise AssertionError(
                _("Cannot specify '__all__' and Member Types together")
            )
        for member_type in CompanyMemberType:
            if member_type not in pref_keys:
                raise AssertionError(
                    _(
                        "Notification preference not defined for {member_type}"
                    ).format(member_type=CompanyMemberType(member_type).label)
                )
        return True

    for notification_type in BaseNotificationManager.__subclasses__():
        check_pref(notification_type.visibility)
        check_pref(notification_type.push)
        check_pref(notification_type.email)
        check_pref(notification_type.sms)
        uid = notification_type.notification_uid
        if not uid:
            raise AssertionError(
                _(
                    "Blank 'notification_uid' for {notif_name}. "
                    "notification_uid cannot be blank"
                ).format(notif_name=notification_type.__name__)
            )
        elif uid in NOTIFICATION_TYPES.keys():
            raise AssertionError(
                _(
                    f"notification_uid should be Unique. "
                    f"The value '{uid}' is already in use."
                )
            )
        NOTIFICATION_TYPES[uid] = notification_type
