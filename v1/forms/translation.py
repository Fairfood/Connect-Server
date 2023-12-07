from modeltranslation.translator import TranslationOptions
from modeltranslation.translator import translator

from . import models


class FormFieldTranslateFields(TranslationOptions):
    fields = ("label",)


translator.register(models.FormField, FormFieldTranslateFields)
