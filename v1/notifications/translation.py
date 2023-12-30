from modeltranslation.translator import TranslationOptions
from modeltranslation.translator import translator

from v1.notifications import models as noti_models

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


class NotificationTranslateFields(TranslationOptions):
    """Translation options for the Notification model fields.

    This class defines which fields of the Notification model should be
    translated.
    """

    fields = (
        "title",
        "body",
    )


translator.register(noti_models.Notification, NotificationTranslateFields)
