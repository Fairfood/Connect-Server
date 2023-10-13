"""Models of the app entities."""

import datetime
from hashid_field.field import Hashid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from base.authentication import utilities as auth_utils
from base.authentication import session
from base.db.models import AbstractBaseModel, Address, NumberedModel
from base.db.utilities import get_file_path
from utilities import functions as utils_functions
from functools import partial
from utilities.function_generators import formatter

from v1.accounts import constants as acc_constants
from v1.accounts.models import ValidationToken

from v1.entities import notifications
from v1.entities import constants as entity_consts


class Entity(AbstractBaseModel, Address, NumberedModel):
    """
    Base model for every type of entities.

    Attribs:
        operations(objs): the categories of the entity. like farmer, collector..
        name(char)      : name of the entity.
        registration_no(char) : identification number of the entity.
        type(int)       :type of the entity(company/others)
        contact_name(char): contact person name.
        email(email)    : email of the entity.
        phone(char)     : phone number of the entity.
        description(char): description about the entity.
        image(image)    : image of the entity.
        invited_on(date): entity invited date.
        joined_on(date) : entity joined date into the system.
        status(int)     : current status of the entity.
        verified(bool)  : is the entity verification completed or not.
    """
    name = models.CharField(
        max_length=500, default='', null=True, blank=True,
        verbose_name=_('Entity Name'))
    registration_no = models.CharField(
        max_length=500, default='', null=True, blank=True,
        verbose_name=_('Entity Registartion Number'))
    type = models.IntegerField(
        default=entity_consts.EntityType.COMPANY, 
        choices=entity_consts.EntityType.choices, verbose_name=_('Entity Type'))
    email = models.EmailField(
        max_length=100, blank=True, null=True, verbose_name=_('Email Name'))
    phone = models.CharField(
        max_length=50, default='', null=True, blank=True, verbose_name=_('Phone Number'))
    description = models.CharField(
        max_length=500, default='', null=True, blank=True, verbose_name=_('Description'))
    image = models.ImageField(
        upload_to=get_file_path, null=True, default=None, blank=True,
        verbose_name=_('Photo'))
    invited_by = models.ForeignKey(
        'self', on_delete=models.SET_NULL, related_name='invited_entitys',
        null=True, blank=True, verbose_name=_('Invited By'))
    invited_on = models.DateTimeField(
        null=True, blank=True, default=None, verbose_name=_('Invited Date'))
    joined_on = models.DateTimeField(
        null=True, blank=True, default=None, verbose_name=_('Joining Date'))
    status = models.IntegerField(
        default=entity_consts.EntityStatus.INACTIVE, 
        choices=entity_consts.EntityStatus.choices, 
        verbose_name=_('Entity Current Status'))
    is_verified = models.BooleanField(
        default=False, verbose_name=_('Is Entity Verified'))
    members = models.ManyToManyField(
        'accounts.CustomUser', related_name='entities',
        verbose_name=_('Member Entities'),
        through='entities.EntityMember', through_fields=('entity', 'user'))
    # country = models.ForeignKey(
    #     'catalogs.Country', on_delete=models.SET_NULL,
    #     related_name='located_entitys', null=True, blank=True,
    #     verbose_name=_('Country of Entity'))
    province = models.ForeignKey(
        'catalogs.Province', on_delete=models.SET_NULL,
        related_name='located_entitys', null=True, blank=True, 
        verbose_name=_('Province of Entity'))
    incharge = models.ForeignKey(
        'accounts.CustomUser', null=True, on_delete=models.SET_NULL, 
        blank=True, related_name="managing_entitys", verbose_name=_("Incharge"))
    currency = models.ForeignKey(
        'catalogs.Currency', null=True, on_delete=models.SET_NULL,
        blank=True, related_name="using_entitys", 
        verbose_name=_("Default Currency"))

    def __str__(self):
        """Object name in django admin."""
        return f'{self.name} - {self.type}'

    @property
    def country(self):
        if self.province:
            return self.province.country
        return None

    @property
    def profile_completion(self):
        total = 0
        filled = 0
        for field in entity_consts.COMPANY_PROFILE_FIELDS:
            if type(field) == str:
                value = getattr(self, field)
                total += 1
                if value:
                    filled += 1
            elif type(field == dict):
                for fk, sub_keys in field.items():
                    if not getattr(self, fk, None):
                        total += len(sub_keys)
                        continue
                    for sub_key in sub_keys:
                        value = getattr(getattr(self, fk), sub_key)
                        total += 1
                        if value:
                            filled += 1
        return int(utils_functions.percentage(filled, total))

    def can_be_edited_by(self, entity=None):
        entity = entity or auth_utils.get_current_entity()
        if not entity:
            return False
        if self.status != entity_consts.EntityStatus.INACTIVE:
            return False
        if self.invited_by != entity:
            return False
        return True


class EntityMember(AbstractBaseModel):
    """
    Model saves members under entities.

    Attribs:
        user(obj)       : user account object of the entity member.
        entity(obj)       : entity which the member is related.
        type(int)       : member type of the entity member like admin, 
            operator...
        active(bool)    : is the unit still active or not.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    user = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.CASCADE, 
        related_name='member_entitys', verbose_name=_('Member User'))
    entity = models.ForeignKey(
        'entities.Entity', on_delete=models.CASCADE, 
        related_name='entity_members', verbose_name=_('Entity'))
    type = models.IntegerField(
        default=entity_consts.EntityMemberType.ADMIN, 
        choices=entity_consts.EntityMemberType.choices, 
        verbose_name=_('Member Type'))
    is_active = models.BooleanField(
        default=True, verbose_name=_('Is Member Active'))
    

    def __str__(self):
        """Object name in django admin."""
        return f'{self.user.name} - {self.entity.name} - \
            {self.type}'

    class Meta:
        unique_together = ('entity', 'user')

    def send_invite(self):
        token = None
        user = self.user
        if not user.password or not user.has_usable_password():
            token = ValidationToken.initialize(
                user, acc_constants.ValidationTokenType.INVITE)
        notification_manager = notifications.MemberInviteNotificationManager(
            user=user, action_object=self, token=token)
        notification_manager.send_notification()

    def get_notification_pref(self, notif_manager):
        """
        Function to return notification preferences for a user.
        """
        from v1.notifications.constants import NotificationCondition
        def get_pref(config: dict) -> bool:
            if self.type not in config.keys():
                raise ValueError(_("Config not defined."))
            if config[self.type] == NotificationCondition.ENABLED:
                return True
            elif config[self.type] == NotificationCondition.DISABLED:
                return False
            elif config[self.type] == NotificationCondition.IF_USER_ACTIVE:
                return self.user.status == acc_constants.UserStatus.ACTIVE
            return False

        prefs = {
            "visibility": get_pref(notif_manager.visibility),
            "push": get_pref(notif_manager.push),
            "email": get_pref(notif_manager.email),
            "sms": get_pref(notif_manager.sms)
        }
        return prefs


class EntityDocument(AbstractBaseModel):
    """
    Table to save documents of entities.

    Atribs:
        entity(obj)    : entity which the member is related.
        name(str): name of the file
        description(str): description about the document.
        file(file): file.
        is_deleted(bool) : Check to move a file into deleted files section.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    entity = models.ForeignKey(
        'entities.Entity', on_delete=models.CASCADE, verbose_name=_('Entity'), 
        related_name='documents', null=True, blank=True)
    name = models.CharField(
        default='', null=True, blank=True, max_length=500, verbose_name=_('File Name'))
    description = models.CharField(
        default='', null=True, blank=True, max_length=2000, verbose_name=_('File Description'))
    file = models.FileField(
        upload_to=get_file_path,
        null=True, default=None, blank=True, max_length=500, 
        verbose_name=_('Document'))
    category = models.ForeignKey(
        'catalogs.Category', on_delete=models.SET_NULL,
        verbose_name=_('Document Category'), related_name='entities', null=True, 
        blank=True)
    is_deleted = models.BooleanField(
        default=False, verbose_name=_('Is File Deleted'))

    @property
    def file_url(self):
        """Get file url name."""
        try:
            return self.file.url
        except:
            None

    def __str__(self):
        """Object name in django admin."""
        return f'{self.name} - {self.id}'

    def notify(self):
        """Notify the entity members."""
        for user in self.entity.members.all():
            notification_manager = notifications.EntityDocumentNotificationManager(
                user=user, action_object=self, token=None)
            notification_manager.send_notification()
        return True
