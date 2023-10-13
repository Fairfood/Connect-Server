"""Constants under the entities section are stored here."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class EntityType(models.IntegerChoices):
    COMPANY = 101, _('Company')


class EntityStatus(models.IntegerChoices):
    ACTIVE = 101, _('Active')
    INACTIVE = 111, _('Inactive')


class EntityMemberType(models.IntegerChoices):
    SUPER_ADMIN = 101, _('Super Admin')
    ADMIN = 111, _('Admin')
    REPORTER = 141, _('Reporter')


class EntityDocumentType(models.IntegerChoices):
    COMPANY_DOCUMENT = 101, _('Company Document')
    INCORPORATION_DOCUMENT = 102, _('Incorporation Document')
    CERTIFICATION = 103, _('Certification')
    ANNUAL_REPORT = 104, _('Annual Report')


COMPANY_PROFILE_FIELDS = ['name', 'description', 'street', 'city', 'province',
                          'country', 'image', 'registration_no', 'phone', 'email', 
                          'contact_name', 'sub_province',]
