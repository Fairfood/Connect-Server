"""Utility functions for translations."""
from django.conf import settings
from django.utils import translation
from django.utils.translation import gettext_lazy as _


def internationalize_attribute(obj, field_name, text, params=None):
    """Function to set values for a field with localization enabled."""
    curr_language = translation.get_language()
    params = params or {}
    for language in settings.LANGUAGES:
        lang_code = language[0]
        field_suffix = lang_code.replace("-", "_")
        locale_field_name = field_name + "_" + field_suffix
        translation.activate(lang_code)
        text_final = text() if callable(text) else text
        locale_text = _(text_final).format(**params)
        setattr(obj, locale_field_name, locale_text)
    translation.activate(curr_language)
