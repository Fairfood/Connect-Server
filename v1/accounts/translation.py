from modeltranslation.translator import TranslationOptions
from modeltranslation.translator import translator

from v1.accounts import models as user_models

"""
As per the Translation option class registered
each model will create a migration , which will be
invisible in the models.py but shall be reflected in the
migrations:

Any change made in this translation.py file will be
reflected on the next makemigration

It is suggested to not use inheritance of options class
and to create individual option field classes and to be
passed with each models when registering to translate
"""


class PrivacyPolicyTranslateFields(TranslationOptions):
    """Translation options for the PrivacyPolicy model fields.

    This class defines which fields of the PrivacyPolicy model should be
    translated.
    """

    fields = ("content",)


translator.register(user_models.PrivacyPolicy, PrivacyPolicyTranslateFields)
