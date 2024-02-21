"""Models of the app Accounts."""
import datetime

import pendulum
from django.conf import settings
from django.contrib.auth.models import AbstractUser as DjangoAbstractUser
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from base.db import utilities as db_utils
from base.db.models import AbstractBaseModel
from utilities import functions as util_functions
from v1.accounts import constants as user_consts
from v1.apiauth import notifications
from v1.supply_chains import constants as sc_constants


class CustomUser(DjangoAbstractUser, AbstractBaseModel):
    """Base User model.

    Attribs:
        dob(date): Date of birth of user.
        phone (str): phone number of the user.
        address(str): address of the user.
        language(int): Language preference.
        image (img): user image.
        type (int): Type of the user like
            admin ,entity user etc.
        status(int): Current status of the user like created or active.
        blocked(bool): field which shows the active status of user.
        updated_email(email): While updating email the new email is stored
            here before email verification.

    Inherited Attribs:
        username(char): Username for the user for login.
        email(email): Email of the user.
        password(char): Password of the user.
        first_name(char): First name of the user.
        last_name(char): Last name of the user.
        date_joined(date): User added date.
    """

    dob = models.DateField(
        null=True, blank=True, verbose_name=_("Date Of Birth")
    )
    phone = models.CharField(
        default="",
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("Phone Number"),
    )
    address = models.CharField(
        default="",
        max_length=2000,
        null=True,
        blank=True,
        verbose_name=_("Address"),
    )
    language = models.CharField(
        max_length=10,
        verbose_name=_("Selected Language"),
        default=user_consts.Language.ENGLISH,
        choices=user_consts.Language.choices,
    )
    image = models.ImageField(
        upload_to=db_utils.get_file_path,
        null=True,
        default=None,
        blank=True,
        verbose_name=_("Photo"),
    )
    type = models.IntegerField(
        default=user_consts.UserType.ENTITY_USER,
        choices=user_consts.UserType.choices,
        verbose_name=_("User Type"),
    )
    status = models.IntegerField(
        default=user_consts.UserStatus.CREATED,
        choices=user_consts.UserStatus.choices,
        verbose_name=_("User Status"),
    )
    is_blocked = models.BooleanField(
        default=False, verbose_name=_("Block User")
    )
    updated_email = models.EmailField(
        null=True, blank=True, default="", verbose_name=_("Last Updated Email")
    )
    default_entity = models.ForeignKey(
        "supply_chains.Company",
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        verbose_name=_("Default Entity Of User"),
        related_name="default_entity_users",
    )
    accepted_policy = models.ForeignKey(
        "accounts.PrivacyPolicy",
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        verbose_name=_("Latest Accepted Privacy Policy"),
        related_name="accepted_users",
    )
    force_logout = models.BooleanField(
        default=False, verbose_name=_("Force Logout User")
    )

    class Meta:
        """Meta class for the above model."""

        verbose_name = "Base User"

    def __str__(self):
        """Object name in django admin."""
        return f"{self.name} - {self.id}"

    def save(self, *args, **kwargs):
        """Overrides save method."""
        if self.email:
            self.username = self.email
        else:
            self.username = get_random_string(32)
        return super(CustomUser, self).save(*args, **kwargs)

    @property
    def is_admin(self):
        """Check if user is admin."""
        return self.type in [
            user_consts.UserType.ADMIN,
            user_consts.UserType.SUPER_ADMIN,
        ]

    @property
    def image_url(self):
        """Get file url ."""
        try:
            return self.image.url
        except AttributeError:
            return None

    @property
    def name(self):
        """Get user full name."""
        return f"{self.get_full_name()}"

    def get_default_entity(self):
        """Get the default entity."""
        def_entity = self.default_entity
        if not def_entity or def_entity not in self.entities.all():
            self.default_entity = self.entities.all().first()
            self.save()
        return self.default_entity

    def set_default_entity(self, entity):
        """Set the default entity."""
        if self.status == user_consts.UserStatus.ACTIVE:
            entity.status = sc_constants.EntityStatus.ACTIVE
            entity.save()
        self.default_entity = entity
        self.save()
        return self.default_entity

    def reset_password(self, ip="", location="", device=""):
        """Function to set password."""
        token = ValidationToken.initialize(
            self,
            user_consts.ValidationTokenType.RESET_PASS,
            ip,
            location,
            device,
        )
        notification_manager = notifications.PasswordResetNotificationManager(
            user=self, action_object=token, token=token
        )
        notification_manager.send_notification()
        return True

    def set_active(self):
        """Set status of the account."""
        self.status = user_consts.UserStatus.ACTIVE
        self.save()
        def_entity = self.get_default_entity()
        def_entity.status = sc_constants.EntityStatus.ACTIVE
        def_entity.joined_on = pendulum.now()
        def_entity.save()

    @property
    def policy_accepted(self):
        """Return privacy info related to the user."""
        if self.accepted_policy == PrivacyPolicy.current_privacy_policy():
            return True
        return False

    def make_force_logout(self):
        """Method makes force logout true."""
        self.force_logout = True
        self.save()
        return True

    def disable_force_logout(self):
        """Method to make force logout false."""
        self.force_logout = False
        self.save()
        return True

    def get_notification_pref(self, notif_manager):
        """Function to return notification preferences for a user."""
        from v1.notifications.constants import NotificationCondition

        def get_pref(config: dict) -> bool:
            if "__all__" not in config.keys():
                raise ValueError(_("Config not defined."))
            if config["__all__"] == NotificationCondition.ENABLED:
                return True
            elif config["__all__"] == NotificationCondition.DISABLED:
                return False
            elif config["__all__"] == NotificationCondition.IF_USER_ACTIVE:
                return self.status == user_consts.UserStatus.ACTIVE
            return False

        prefs = {
            "visibility": get_pref(notif_manager.visibility),
            "push": get_pref(notif_manager.push),
            "email": get_pref(notif_manager.email),
            "sms": get_pref(notif_manager.sms),
        }
        return prefs

    def is_device_active(self, registration_id):
        """Check if user has active device."""
        return (
            UserDevice.active_devices(self)
            .filter(registration_id=registration_id)
            .exists()
        )


class ValidationToken(AbstractBaseModel):
    """Class to store the validation token data.

    This is a generic model to store and validate all
    sort of tokens including password setters, one time
    passwords and email validations..

    Attribs:
        user(obj): user object
        key (str): token.
        status(int): status of the validation token
        expiry(datetime): time up to which link is valid.
        type(int): type indicating the event associated.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="validation_tokens",
        verbose_name=_("Token User"),
        null=True,
        blank=True,
    )

    ip = models.CharField(default="", max_length=500, blank=True)
    location = models.CharField(default="", max_length=500, blank=True)
    device = models.CharField(default="", max_length=500, blank=True)

    key = models.CharField(max_length=200, verbose_name=_("Token"))
    status = models.IntegerField(
        default=user_consts.ValidationTokenStatus.UNUSED,
        choices=user_consts.ValidationTokenStatus.choices,
        verbose_name=_("Token Status"),
    )
    expiry = models.DateTimeField(
        default=timezone.now, verbose_name=_("Token Expiry Date")
    )
    type = models.IntegerField(
        default=user_consts.ValidationTokenType.VERIFY_EMAIL,
        choices=user_consts.ValidationTokenType.choices,
        verbose_name=_("Token Type"),
    )

    def __str__(self):
        """Object name in django admin."""
        return f"{self.user.name} : {self.key} :  {self.id.hashid}"

    def save(self, *args, **kwargs):
        """Overriding the default save signal.

        This function will generate the token key based on the type of
        the token and save when the save() function is called if the key
        is empty. It. will. also set the expiry when the object is
        created for the first time.
        """
        if not self.key:
            self.key = self.generate_unique_key()
        if not self.id:
            self.expiry = self.get_expiry()
        return super(ValidationToken, self).save(*args, **kwargs)

    @property
    def creation_time_str(self):
        """returns the creation time."""
        return pendulum.instance(self.created_on).format(
            "hh:mm A on dddd, DD-MM-YYYY"
        )

    def get_validity_period(self):
        """Returns the validity period."""
        return user_consts.TOKEN_VALIDITY[self.type]

    def get_expiry(self):
        """Function to get the validity based on type."""
        validity = self.get_validity_period()
        return timezone.now() + datetime.timedelta(minutes=validity)

    def generate_unique_key(self):
        """Function to generate unique key."""
        if self.type != user_consts.ValidationTokenType.OTP:
            key = get_random_string(settings.ACCESS_TOKEN_LENGTH)
        else:
            key = util_functions.generate_random_number(settings.OTP_LENGTH)

        if ValidationToken.objects.filter(
            key=key,
            type=self.type,
            status=user_consts.ValidationTokenStatus.UNUSED,
        ).exists():
            key = self.generate_unique_key()
        return key

    def validate(self):
        """Function to.

        validate the token.
        """
        status = True
        if not self.is_valid:
            status = False
        self.status = user_consts.ValidationTokenStatus.USED
        self.updater = self.user
        self.save()
        return status

    def refresh(self):
        """Function  to refresh the validation token."""
        if not self.is_valid:
            self.key = self.generate_unique_key()
            self.status = user_consts.ValidationTokenStatus.UNUSED
        self.expiry = self.get_expiry()
        self.updater = self.user
        self.save()
        return True

    def mark_as_used(self):
        """Function to mark validation token as used."""
        self.status = user_consts.ValidationTokenStatus.USED
        self.save()

    @staticmethod
    def initialize(user, type, ip="", location="", device=""):
        """Function to initialize verification."""
        token = ValidationToken.objects.create(
            user=user,
            status=user_consts.ValidationTokenStatus.UNUSED,
            type=type,
        )
        token.ip = ip
        token.location = location
        token.device = device
        token.save()
        return token

    @property
    def validity(self):
        """Function to get the validity of token."""
        return util_functions.date_time_desc(self.expiry)

    @property
    def created_on_desc(self):
        """Function to get the validity of token."""
        return util_functions.date_time_desc(self.created_on)

    def is_valid(self):
        """Function  which check if Validator is valid."""
        if self.expiry > timezone.now() and (
            self.status == user_consts.ValidationTokenStatus.UNUSED
        ):
            return True
        return False

    def invalidate(self):
        """Function chnage the status of the token into used and change the
        expiry date of the token."""
        self.mark_as_used()
        self.expiry = timezone.now()
        self.save()
        return True


# class UserDevice(AbstractFCMDevice, AbstractBaseModel):
class UserDevice(AbstractBaseModel):
    """Class for user devices.

    This is inherited from the AbstractFCMDevice and
    AbstractBaseModel.

    Attribs:
        user(obj): user object.
        type(int): device types
    Attribs Inherited:
        name(str): name of the device
        active(bool): bool value.
        date_created(datetime): created time.
        device_id(str): Device id
        registration_id(str): Reg id
    """

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name=_("Device User"),
        related_name="devices",
        null=True,
        blank=True,
    )
    type = models.IntegerField(
        default=user_consts.DeviceType.ANDROID,
        choices=user_consts.DeviceType.choices,
        verbose_name=_("Device Type"),
    )
    registration_id = models.TextField(
        verbose_name=_("Registration token"), blank=True, default=""
    )
    active = models.BooleanField(
        verbose_name=_("Is active"),
        default=True,
    )
    device_name = models.CharField(
        max_length=255,
        verbose_name=_("Device Name"),
        blank=True,
        null=True,
    )
    device_loc = models.CharField(
        max_length=255,
        verbose_name=_("Device Location"),
        blank=True,
        null=True,
    )

    class Meta:
        """Meta data."""

        verbose_name = _("User device")
        verbose_name_plural = _("User devices")

    def deactivate(self, types=user_consts.MOBILE_DEVICE_TYPES):
        """To deactivate this device."""
        self.active = False
        self.save()

    @classmethod
    def active_devices(cls, user):
        """List users active devices."""
        return cls.objects.filter(
            user=user,
            active=True,
        )

    @classmethod
    def deactivate_devices(cls, user):
        """Deactivate all devices of a user."""
        devices = cls.active_devices(user)
        for device in devices:
            device.deactivate()

    @classmethod
    def get_device_with_device_id(cls, device_id, user):
        """Get device with device id."""
        return cls.objects.filter(registration_id=device_id, user=user).first()


class PrivacyPolicy(AbstractBaseModel):
    """Privacy Policy model."""

    content = models.TextField(
        default="", blank=True, null=True, verbose_name=_("Policy Content")
    )
    version = models.PositiveIntegerField(
        default=0, verbose_name=_("Version"), unique=True
    )
    date = models.DateField(
        default=datetime.date.today,
        blank=True,
        null=True,
        verbose_name=_("Privacy Policy Date"),
    )
    since = models.DateField(
        default=datetime.date.today,
        blank=True,
        null=True,
        verbose_name=_("Start Date"),
    )

    class Meta:
        """Meta data."""

        verbose_name_plural = _("Privacy Policies")

    def __str__(self):
        """Object value django admin."""
        return f"{self.version} : {self.since} - {self.id}"

    @staticmethod
    def latest_privacy_policy():
        """Return latest privacy policy."""
        return PrivacyPolicy.objects.latest("id")

    @staticmethod
    def current_privacy_policy():
        """Return current privacy policy."""
        policies = PrivacyPolicy.objects.exclude(
            since__gt=datetime.date.today()
        )
        if policies.exists():
            return policies.latest("version")
