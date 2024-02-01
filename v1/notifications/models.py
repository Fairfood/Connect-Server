"""Notification Models."""
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from base.db.models import AbstractBaseModel
from utilities import email
from utilities import sms


class Notification(AbstractBaseModel):
    """A class for managing user notifications.

    Attributes:
        user (UserModel): The user associated with the notification.
        is_read (bool): Indicates whether the notification has been read by
            the user.
        visibility (bool): Indicates if the notification is visible.
        title (str): The title of the notification.
        body (str): The content of the notification.
        action_url (str): URL related to the notification action.
        actor_entity (Company): The company that initiated the action.
        target_entity (Company): The company that is the target of
            the notification.
        action_push (bool): Whether to send push notifications for this action.
        action_sms (bool): Whether to send SMS notifications for this action.
        action_email (bool): Whether to send email notifications for this
            action.
        event_type (ContentType): The content type of the related event.
        event_id (int): The ID of the related event.
        event (GenericForeignKey): A reference to the related event.
        redirect_id (int): The ID used for redirection.
        redirect_type (str): The type of redirection.
        type (str): The type of notification for identification.
        context (dict): Additional context for the notification.
        send_to (str): Email address to send the notification.
        validation_token (ValidationToken): Validation token related to
            the notification.
        aws_sms_id (str): ID for AWS SMS service.

    Meta:
        ordering: Specifies the default ordering for notifications.

    Methods:
        send_email: Sends an email notification.
        send_push: Sends a push notification.
        send_sms: Sends an SMS notification.
        send: Sends the notification via all available channels.
        read: Marks the notification as read.
        notification_manager: Returns the notification manager based on the
            notification type.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("User"),
    )
    is_read = models.BooleanField(default=False, verbose_name=_("Is read?"))
    visibility = models.BooleanField(
        default=True, verbose_name=_("Visibility")
    )
    title = models.CharField(max_length=300, verbose_name=_("Title"))
    body = models.CharField(max_length=500, verbose_name=_("Body"))

    action_url = models.CharField(
        max_length=500, blank=True, verbose_name=_("Action URL")
    )

    actor_entity = models.ForeignKey(
        "supply_chains.Company",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="actions",
        verbose_name=_("Actor Entity"),
    )
    target_entity = models.ForeignKey(
        "supply_chains.Company",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="notifications",
        verbose_name=_("Target Entity"),
    )

    action_push = models.BooleanField(
        default=False, verbose_name=_("Push Notification")
    )
    action_sms = models.BooleanField(
        default=False, verbose_name=_("Sms Notification")
    )
    action_email = models.BooleanField(
        default=False, verbose_name=_("Email Notification")
    )

    event_type = models.ForeignKey(
        ContentType,
        related_name="notification_event_types",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Event Type"),
    )
    event_id = models.PositiveIntegerField(null=True, blank=True)
    event = GenericForeignKey("event_type", "event_id")

    redirect_id = models.PositiveIntegerField(
        null=True, blank=True, default=None, verbose_name=_("Redirect ID")
    )
    redirect_type = models.CharField(
        max_length=200, blank=True, null=True, verbose_name=_("Redirect type")
    )

    type = models.CharField(max_length=100, verbose_name=_("Type"))

    context = models.JSONField(
        null=True, blank=True, verbose_name=_("Context")
    )
    send_to = models.EmailField(
        null=True, blank=True, verbose_name=_("Send To")
    )

    validation_token = models.OneToOneField(
        "accounts.ValidationToken",
        on_delete=models.SET_NULL,
        related_name="notification",
        null=True,
        blank=True,
        verbose_name=_("Validation Token"),
    )

    aws_sms_id = models.CharField(
        max_length=100, null=True, blank=True, verbose_name=_("AWS SMS ID")
    )

    class Meta:
        """Meta class for the above model."""

        ordering = ("-created_on",)

    def __str__(self):
        """Function to return value in django admin."""
        return "%s - %s | %s" % (self.user.name, self.title, self.id)

    def send_email(self):
        """Sends an email notification.

        This method sends an email notification to the user. It uses the
        email template specified by the notification manager and
        includes relevant context.
        """
        notification_manager = self.notification_manager()
        if not self.action_email:
            return False

        curr_language = translation.get_language()
        translation.activate(self.user.language)

        template_name = notification_manager.email_template

        render_context = {
            "action_object": self.event,
            "notification": self,
            "context": self.context,
            "action_text": notification_manager.action_text,
        }
        html = render_to_string(
            template_name=template_name, context=render_context
        )
        email.send_email.delay(
            subject=self.title, to_email=self.send_to, html=html
        )
        translation.activate(curr_language)
        return True

    def send_push(self):
        """Sends a push notification.

        This method is responsible for sending push notifications.
        """
        raise NotImplementedError("Push notifications are not implemented.")

    def send_sms(self):
        """Sends an SMS notification.

        This method sends an SMS notification to the user if the
        'action_sms' flag is set to True and the user's phone number is
        valid.
        """
        if (
            not self.action_sms
            or not self.user.phone
            or len(self.user.phone) < 7
        ):
            return False
        self.aws_sms_id = sms.send_sms.delay(self.user.phone, self.body)
        self.save()
        return True

    def send(self):
        """Sends the notification via all available channels.

        This method orchestrates the sending of a notification via
        email, push notification, and SMS. It returns True if at least
        one of these channels successfully sends the notification.
        """
        self.send_email()
        self.send_push()
        self.send_sms()
        return True

    def read(self):
        """Marks the notification as read.

        This method sets the 'is_read' attribute to True, indicating
        that the user has read the notification.
        """
        self.is_read = True
        self.save()

    def notification_manager(self):
        """Returns the notification manager based on the notification type.

        This method returns the appropriate notification manager based
        on the 'type' attribute of the notification. The notification
        manager is used to customize the notification's behavior.
        """
        from .manager import NOTIFICATION_TYPES

        return NOTIFICATION_TYPES[self.type]


class SMSAlerts(AbstractBaseModel):
    """Model to track all the SMSs sent and log the response.

    Attributes:
        phone (str): The phone number to which the SMS is sent.
        message (text): The message content of the SMS.
        response (json): The response received from the SMS API.
        response_text (text): The response received in case of an error.
    """

    phone = models.CharField(max_length=20)
    message = models.TextField(null=True, blank=True)
    response = models.JSONField(null=True, blank=True)
    response_text = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.phone}"
