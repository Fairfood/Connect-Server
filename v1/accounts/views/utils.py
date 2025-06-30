from base.exceptions.custom_exceptions import BadRequest
from base.request_handler.response import SuccessResponse
from base.request_handler.views import IDDEcodeScopeViewset
from utilities.country_data import COUNTRY_LIST, COUNTRY_WITH_PROVINCE


class CountryListView(IDDEcodeScopeViewset):
    """
    View for listing all countries.

    This view returns a list of all country names.
    The response structure is a simple JSON array of country names:
    Example:
    [
        "USA",
        "Canada",
        "India"
    ]
    """
    resource_types = ["user"]
    http_method_names = ("get",)
    def list(self, request, *args, **kwargs):
        return SuccessResponse(COUNTRY_LIST)


class CountryWithProvincesListView(IDDEcodeScopeViewset):
    """
    View for listing countries and their provinces.

    This view returns a list of countries, with each country being represented by a dictionary.
    Each dictionary contains a country name and a list of provinces associated with that country.
    The response format is:
    [
        {
            "country": "USA",
            "provinces": ["California", "Texas", "New York"]
        },
        {
            "country": "Canada",
            "provinces": ["Ontario", "Quebec", "British Columbia"]
        }
    ]
    """
    resource_types = ["user"]
    http_method_names = ("get",)

    def list(self, request, *args, **kwargs):
        countries = []
        for country, provinces in COUNTRY_WITH_PROVINCE.items():
            countries.append({"country": country, "provinces": provinces})
        return SuccessResponse(countries)

    def retrieve(self, request, *args, **kwargs):
        country = kwargs.get("country_name", None)
        if country and country in COUNTRY_WITH_PROVINCE:
            return SuccessResponse(COUNTRY_WITH_PROVINCE[country])
        raise BadRequest("Invalid country name.")
