import json
import os

from django.conf import settings

from v1.catalogs.models.common_models import Currency


def load_currencies():
    """Load currency data from a JSON file into the Currency model.

    Reads currency data from a JSON file located in the 'fixtures' directory
    and updates or creates Currency objects in the database based on the
    provided data.

    The JSON file should have an array of objects, where each object represents
    a currency with 'name' and 'code' properties.

    Example JSON structure:
    [
        {"name": "United States Dollar", "code": "USD"},
        {"name": "Euro", "code": "EUR"},
        ...
    ]

    Existing Currency objects with matching 'code' are updated with the
    corresponding 'name'. New Currency objects are created if no matching
    'code' is found.
    """
    file_path = os.path.join(settings.BASE_DIR, "fixtures", "currencies.json")
    with open(file_path, "r") as file:
        currencies = json.load(file)
        update_list = []
        create_list = []
        for currency in currencies:
            try:
                obj = Currency.objects.get(code=currency["code"])
                obj.name = currency["name"]
                update_list.append(obj)
            except Currency.DoesNotExist:
                data = {
                    "name": currency["name"],
                    "code": currency["code"],
                }
                create_list.append(Currency(**data))

        if update_list:
            Currency.objects.bulk_update(update_list, ["name"])
        if create_list:
            Currency.objects.bulk_create(create_list)
    print("Currencies loaded")


def run():
    """Entry point function to execute tasks.(compactable with runscript)

    This function serves as an entry point for running tasks or
    operations. Currently, it calls the 'load_currencies' function.
    """
    load_currencies()
