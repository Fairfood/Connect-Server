"""
Notification Models
"""

from django.db import models
from django.utils import translation
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from base.db.models import AbstractBaseModel

from utilities import email
from utilities import sms


class Notification(AbstractBaseModel):
    """
    Class for managing user notification.

    Attribs:
        user(obj): User object
        is_read(bool): to mark if the notification is
            read by the user.
        title_en(str): notification message title in English.
        body_en(str): notification message body in English
        title_loc(str): notification message title in local language.
        body_loc(str): notification message body in local language
        action(int): notification type based on which
            sending emails or push notification is decided.
        event(int): notification event
        event_id(int): event id.
        type(int): notification type for identifying the notification
            when it is pushed to devices.
    """

    user = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    visibility = models.BooleanField(default=True)
    title = models.CharField(default='', max_length=300)
    body = models.CharField(default='', max_length=500)

    action_url = models.CharField(default='', max_length=500, blank=True)

    actor_entity = models.ForeignKey(
        'entities.Entity', on_delete=models.CASCADE, blank=True, null=True,
        related_name='actions')
    target_entity = models.ForeignKey(
        'entities.Entity', on_delete=models.CASCADE, blank=True, null=True,
        related_name='notifications')

    action_push = models.BooleanField(default=False)
    action_sms = models.BooleanField(default=False)
    action_email = models.BooleanField(default=False)

    event_type = models.ForeignKey(
        ContentType, related_name="notification_event_types", 
        on_delete=models.SET_NULL, null=True)
    event_id = models.PositiveIntegerField(null=True, blank=True)
    event = GenericForeignKey('event_type', 'event_id')
    redirect_id = models.PositiveIntegerField(
        null=True, blank=True, default=None)
    redirect_type = models.CharField(
        max_length=200, blank=True, null=True, default='')

    type = models.CharField(max_length=100)

    context = models.JSONField(null=True, blank=True)
    send_to = models.EmailField(null=True, blank=True, default='')

    validation_token = models.OneToOneField(
        'accounts.ValidationToken', on_delete=models.SET_NULL,
        related_name='notification', null=True, blank=True)

    aws_sms_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        """Meta class for the above model."""

        ordering = ('-created_on',)

    def __str__(self):
        """Function to return value in django admin."""
        return '%s - %s | %s' % (self.user.name, self.title, self.id)

    def send_email(self):
        notification_manager = self.notification_manager()
        if not self.action_email:
            return False

        curr_language = translation.get_language()
        translation.activate(self.user.language)

        template_name = notification_manager.email_template

        render_context = {
            'action_object': self.event,
            'notification': self,
            'context': self.context,
            'action_text': notification_manager.action_text
        }
        html = render_to_string(template_name=template_name, context=render_context)
        email.send_email.delay(
            subject=self.title, to_email=self.send_to, html=html
        )
        translation.activate(curr_language)
        return True

    def send_push(self):
        pass

    def send_sms(self):
        if not self.action_sms or not self.user.phone or len(self.user.phone) < 7:
            return False
        self.aws_sms_id = sms.send_sms.delay(self.user.phone, self.body)
        self.save()
        return True

    def send(self):
        """Send notification."""
        self.send_email()
        self.send_push()
        self.send_sms()
        return True

    def read(self):
        """Function to read notification."""
        self.is_read = True
        self.save()

    def notification_manager(self):
        from .manager import NOTIFICATION_TYPES
        return NOTIFICATION_TYPES[self.type]


class SMSAlerts(AbstractBaseModel):
    """
    Model to track all the SMSs sent and log the response

    Attributes:
        phone(str)          : The phone number to send SMS to.
        message(text)       : The message to send.
        response(json)      : The response received from SMS API.
        response_text(text) : The response received in case of error.
    """

    phone = models.CharField(max_length=20)
    message = models.TextField(null=True, blank=True)
    response = models.JSONField(null=True, blank=True)
    response_text = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.phone}"
