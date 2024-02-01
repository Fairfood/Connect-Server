"""Models of the app entities."""
from django.db import models
from django.db import transaction
from django.forms import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from . import base_models
from .. import constants as sc_consts
from base.authentication import utilities as auth_utils
from base.db import models as abstarct_models
from v1.catalogs.models.product_models import Premium
from v1.forms import constants as form_consts
from v1.forms.models import Form


class AbstractCompanyModel(
    abstarct_models.AbstractAddressModel,
    abstarct_models.AbstractContactModel,
    base_models.Entity,
):
    """An abstract base model for a company, providing fields for basic company
    information such as address, contact details, and a unique identifier."""

    class Meta:
        abstract = True


class Company(AbstractCompanyModel):
    """Model representing a company entity.

    This model is used to represent a company entity within the system. It
    contains fields for the company's name, registration number, members,
    incharge, and default currency.

    Attributes:
        name (str): The name of the company.
        registration_no (str): The registration number of the company.
        members (ManyToManyField): The members associated with the company.
        incharge (ForeignKey): The user who is in charge of the company.
        currency (ForeignKey): The default currency used by the company.
        premiums (ManyToManyField): The premiums associated with the company.
    """

    name = models.CharField(
        max_length=500,
        verbose_name=_("Company Name"),
    )
    members = models.ManyToManyField(
        "accounts.CustomUser",
        related_name="entities",
        verbose_name=_("Member Companies"),
        through="supply_chains.CompanyMember",
        through_fields=("company", "user"),
    )
    currency = models.ForeignKey(
        "catalogs.Currency",
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        related_name="using_companies",
        verbose_name=_("Default Currency"),
    )
    products = models.ManyToManyField(
        "catalogs.Product",
        through="supply_chains.CompanyProduct",
        related_name="companies",
        verbose_name=_("Products"),
    )
    buy_enabled = models.BooleanField(
        default=True, verbose_name=_("Buy Enabled")
    )
    sell_enabled = models.BooleanField(
        default=False, verbose_name=_("Sell Enabled")
    )
    quality_correction = models.BooleanField(
        default=False, verbose_name=_("Quality Correction")
    )
    allow_multiple_login = models.BooleanField(
        default=True, verbose_name=_("Allow Multiple Login")
    )

    class Meta:
        """Meta class defines class level configurations."""

        verbose_name_plural = _("Companies")

    def __str__(self):
        """Object name in django admin."""
        return f"{self.name}"

    def can_be_edited_by(self, company=None):
        """Check if the entity can be edited by a specified company.

        This method determines whether the entity can be edited by the
        specified company based on various conditions, such as the entity's
        status and the company that initiated the invitation.

        Args:
            company (optional): The company for which the edit permission is
                                checked. If not provided, the current company
                                is used.

        Returns:
            bool: True if the entity can be edited by the specified company,
                  False otherwise.
        """

        company = company or auth_utils.get_current_company()
        checks = (
            not company,
            self.status != sc_consts.EntityStatus.INACTIVE,
            self.invited_by != company,
        )
        if any(checks):
            return False
        return True


class CompanyMember(abstarct_models.AbstractBaseModel):
    """Model saves members under entities.

    Attribs:
        user(obj)       : user account object of the company member.
        company(obj)       : company which the member is related.
        type(int)       : member type of the company member like admin,
            operator...
        active(bool)    : is the unit still active or not.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    user = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="member_companies",
        verbose_name=_("Member User"),
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="company_members",
        verbose_name=_("Company"),
    )
    type = models.CharField(
        max_length=11,
        default=sc_consts.CompanyMemberType.ADMIN,
        choices=sc_consts.CompanyMemberType.choices,
        verbose_name=_("Member Type"),
    )
    is_active = models.BooleanField(
        default=True, verbose_name=_("Is Member Active")
    )

    def __str__(self):
        """Object name in django admin."""
        return f"{self.user.name} - " f"{self.company.name} - " f"{self.type}"

    class Meta:
        unique_together = ("company", "user")

    # def send_invite(self):
    #     token = None
    #     user = self.user
    #     if not user.password or not user.has_usable_password():
    #         token = ValidationToken.initialize(
    #             user, acc_constants.ValidationTokenType.INVITE
    #         )
    #     notification_manager = notifications.MemberInviteNotificationManager(
    #         user=user, action_object=self, token=token
    #     )
    #     notification_manager.send_notification()

    # def get_notification_pref(self, notif_manager):
    #     """Function to return notification preferences for a user."""
    #     from v1.notifications.constants import NotificationCondition

    #     def get_pref(config: dict) -> bool:
    #         if self.type not in config.keys():
    #             raise ValueError(_("Config not defined."))
    #         if config[self.type] == NotificationCondition.ENABLED:
    #             return True
    #         elif config[self.type] == NotificationCondition.DISABLED:
    #             return False
    #         elif config[self.type] == NotificationCondition.IF_USER_ACTIVE:
    #             return self.user.status == acc_constants.UserStatus.ACTIVE
    #         return False

    #     prefs = {
    #         "visibility": get_pref(notif_manager.visibility),
    #         "push": get_pref(notif_manager.push),
    #         "email": get_pref(notif_manager.email),
    #         "sms": get_pref(notif_manager.sms),
    #     }
    #     return prefs


class CompanyProduct(abstarct_models.AbstractBaseModel):
    """Represents the association between a Company and a Product.

    Attributes:
    - company (models.ForeignKey): The Company associated with the Product.
    - product (models.ForeignKey): The Product associated with the Company.
    - form (models.OneToOneField): An optional Form associated with the
        Company-Product relationship.

    Related Names:
    - company_products (related_name): A reverse relation to access
        Company-Product associations for a Company.
    - company_products (related_name): A reverse relation to access
        Company-Product associations for a Product.
    - company_product (related_name): A reverse relation to access the Form
        associated with this Company-Product relationship.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="company_products",
        verbose_name=_("Company"),
    )
    product = models.ForeignKey(
        "catalogs.Product",
        on_delete=models.CASCADE,
        related_name="company_products",
        verbose_name=_("Product"),
    )
    forms = models.ManyToManyField(
        Form,
        related_name="company_products",
        blank=True,
        verbose_name=_("Forms"),
    )
    premiums = models.ManyToManyField(
        Premium,
        related_name="company_products",
        verbose_name=_("Premium"),
        blank=True,
    )
    is_active = models.BooleanField(
        default=True, verbose_name=_("Is Company Product Active")
    )

    def __str__(self):
        return f"{self.company.name} - {self.product.name}"

    @transaction.atomic
    def save(self, *args, **kwargs):
        """Save method for the model.

        This method performs atomic transactions and includes checks
        related to premium removal, form validation, and premium check
        before calling the parent class's save method.
        """

        self._check_premium_removal()
        super().save(*args, **kwargs)
        self._form_check()
        self._premium_check()

    def _form_check(self):
        """Check if the form is valid."""
        if self.forms.exists():
            for form in self.forms.all():
                if form != form_consts.FormType.PRODUCT:
                    raise ValueError(
                        _("Invalid form type. Not a product form.")
                    )

    def _premium_check(self):
        """Check if the premium is valid."""
        errors = []
        for premium in self.premiums.all():
            if premium not in self.company.owned_premiums.all():
                errors.append(
                    f"{premium.name} is not a premium of "
                    f"{self.company.name}."
                )
        if errors:
            raise ValidationError(errors)

    def _check_premium_removal(self):
        """Check if the premium is valid."""
        if self.pk:
            old_premiums = self.__class__.objects.get(
                pk=self.pk
            ).premiums.only("id")
            new_premiums = self.premiums.only("id")
            removed_premiums = old_premiums.exclude(pk__in=new_premiums)
            added_premiums = new_premiums.exclude(pk__in=old_premiums)
            premuims_changed = (
                removed_premiums.exists() or added_premiums.exists()
            )
            if premuims_changed:
                self.product.updated_on = timezone.now()
                self.product.save()


class CompanyFieldVisibilty(abstarct_models.AbstractBaseModel):
    """Model to save field visibilities of a company created Farmers and
    Transactions.

    Attribs:
        name(str)       : name of the field visibility.
        visibility(bool): visibility of the field.
        type(str)       : type of the field like transaction, farmer...
        company(obj)    : company which the field visibility is related.
    """

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    visibility = models.BooleanField(
        default=True, verbose_name=_("Visibility")
    )
    type = models.CharField(
        max_length=11,
        choices=sc_consts.CompanyFieldVisibiltyType.choices,
        default=sc_consts.CompanyFieldVisibiltyType.TRANSACTION,
        verbose_name=_("Type"),
    )
    company = models.ForeignKey(
        "supply_chains.Company",
        on_delete=models.CASCADE,
        related_name="field_visibilities",
        verbose_name=_("Company"),
    )

    def __str__(self):
        return f"{self.name} - {self.company.name}"
