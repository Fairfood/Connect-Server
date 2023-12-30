"""Models are registered with django admin at here."""
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from v1.accounts import models as user_models


deployment = settings.DEPLOYMENT.capitalize()
admin.site.site_header = _("%s RightOrigins Admin" % deployment)
admin.site.site_title = _("RightOrigins: %s Admin Portal" % (deployment))
admin.site.index_title = _("Welcome to RightOrigins %s Portal" % (deployment))


class ValidationTokenAdmin(admin.ModelAdmin):
    """Class view to customize validation token admin."""

    ordering = ("-updated_on",)

    def salt(self, obj):
        """Get salt."""
        return obj.id

    list_display = ("user", "key", "status", "salt", "type", "expiry")
    list_filter = ("type", "status")


class UserDeviceAdmin(admin.ModelAdmin):
    """Class view to customize user device admin.

    This admin class provides customization for the UserDevice model in
    the Django admin interface.
    """

    list_display = ("device_name", "user", "registration_id", "type", "active")
    list_filter = ("active",)

    def has_add_permission(self, request, obj=None):
        """Determine whether the user has permission to add new UserDevice
        instances.

        Args:
            request: The request object.
            obj: The object being viewed or edited.

        Returns:
            bool: True if the user has add permission, False otherwise.
        """
        return False


class CustomUserAdmin(UserAdmin):
    """Overriding user adminto add additional fields."""

    # readonly_fields = ('id', 'default_entity')
    ordering = ("-id",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "updated_email",
                    "dob",
                    "phone",
                    "address",
                    "language",
                    "image",
                )
            },
        ),
        (
            _("Internal values"),
            {
                "fields": ("type", "status", "force_logout"),
            },
        ),
        (
            _("Entity details"),
            {
                "fields": ("default_entity",),
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = (
        "id",
        "first_name",
        "last_name",
        "email",
    )


class PrivacyPolicyAdmin(admin.ModelAdmin):
    """Class view to customize privacy policy in admin."""

    list_display = ("version", "id", "since")


admin.site.register(user_models.CustomUser, CustomUserAdmin)
admin.site.register(user_models.ValidationToken, ValidationTokenAdmin)
admin.site.register(user_models.UserDevice, UserDeviceAdmin)
admin.site.register(user_models.PrivacyPolicy, PrivacyPolicyAdmin)
