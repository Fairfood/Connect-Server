# from modeltranslation.translator import TranslationOptions
# from modeltranslation.translator import translator
# from v1.catalogs.models import common_models as catalog_models
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
# class CountryTranslateFields(TranslationOptions):
#     fields = ('name',)
# class ProvinceTranslateFields(TranslationOptions):
#     fields = ('name',)
# class CurrencyTranslateFields(TranslationOptions):
#     fields = ('name',)
# class CategoryTranslateFields(TranslationOptions):
#     """Translation options for the Category model."""
#     fields = ("name",)
# translator.register(catalog_models.Country, CountryTranslateFields)
# translator.register(catalog_models.Province, ProvinceTranslateFields)
# translator.register(catalog_models.Currency, CurrencyTranslateFields)
# translator.register(catalog_models.Category, CategoryTranslateFields)
