from modeltranslation.translator import TranslationOptions
from modeltranslation.translator import translator

from . import models


class FormFieldTranslateFields(TranslationOptions):
    """Translation options for the 'FormField' model.

    This class defines the translation options for specific fields of
    the 'FormField' model, allowing the translation of the 'label'
    field.
    """

    fields = ("label",)


translator.register(models.FormField, FormFieldTranslateFields)
