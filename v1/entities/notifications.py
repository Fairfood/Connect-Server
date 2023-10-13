from django.utils.translation import gettext_lazy as _

from v1.entities.constants import EntityMemberType
from v1.notifications.constants import NotificationCondition
from v1.notifications.manager import BaseNotificationManager


class MemberInviteNotificationManager(BaseNotificationManager):
    """Notification manager for sending email notification to entity member
    when a entity is invited."""

    notification_uid: str = "member_invite"

    action_text: str = _("Accept invitation")
    url_path: str = "welcome"

    visibility: dict = {"__all__": NotificationCondition.ENABLED}
    push: dict = {"__all__": NotificationCondition.ENABLED}
    email: dict = {"__all__": NotificationCondition.ENABLED}
    sms: dict = {"__all__": NotificationCondition.DISABLED}

    email_template: str = "member_invite.html"

    def get_title(self) -> str:
        return _("Team member invitation from {name}").format(
            name=self.action_object.entity.name
        )

    def get_body(self) -> str:
        return _(
            "You have been invited to trace_connect portal to manage"
            " {entity_name} by {inviter_name}."
        ).format(
            entity_name=self.action_object.entity.name,
            inviter_name=self.action_object.creator.name,
        )

    def get_url_params(self) -> dict:
        return {
            "entity_id": self.action_object.entity.id,
        }

    def get_actor_entity(self):
        return self.action_object.entity

    def get_target_entity(self):
        return self.action_object.entity


class EntityDocumentNotificationManager(BaseNotificationManager):
    """Notification manager for notify entity members that new documents added
    to the under the entity."""

    notification_uid: str = "entity_document_added"

    visibility: dict = {
        EntityMemberType.SUPER_ADMIN: NotificationCondition.ENABLED,
        EntityMemberType.ADMIN: NotificationCondition.ENABLED,
        EntityMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    push: dict = {
        EntityMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        EntityMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        EntityMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    email: dict = {
        EntityMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        EntityMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        EntityMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    sms: dict = {
        EntityMemberType.SUPER_ADMIN: NotificationCondition.DISABLED,
        EntityMemberType.ADMIN: NotificationCondition.DISABLED,
        EntityMemberType.REPORTER: NotificationCondition.DISABLED,
    }

    def get_title(self) -> str:
        return _("New company document added.")

    def get_body(self) -> str:
        return _(
            "New company document added under the category {category}."
        ).format(category=self.action_object.category.name)

    def get_actor_entity(self):
        return self.action_object.entity

    def get_target_entity(self):
        return self.action_object.entity
