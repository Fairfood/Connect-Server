from rest_framework import generics

from base.request_handler.response import SuccessResponse
from utilities.country_data import COUNTRY_LIST, COUNTRY_WITH_PROVINCE


class CountryListView(generics.ListAPIView):
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
    def list(self, request, *args, **kwargs):
        return SuccessResponse(COUNTRY_LIST)


class CountryWithProvincesListView(generics.ListAPIView):
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
    def list(self, request, *args, **kwargs):
        countries = []
        for country, provinces in COUNTRY_WITH_PROVINCE.items():
            countries.append({"country": country, "provinces": provinces})
        return SuccessResponse(countries)
