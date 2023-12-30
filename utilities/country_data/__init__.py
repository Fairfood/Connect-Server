"""Country data The json file country_data_with_province_larlong.json has a
json list of countries, their latlong, dialcode, 2 digit alphabetical code and
subdivision of all the countries.

Format
[

    "<country_name:str>": {
        "latlong": [
            <latitude:float>,
            <longitude:float>
        ],
        "dial_code": "<phonenumber_dialcode_without+:str>",
        "alpha_2": "<2letter_code>",
        "alpha_3": "<3letter_code>",
        "currency": "<3letter_currency_code>",
        "sub_divisions": {
            "<division_name:str>": {
                "latlong": [
                    <latitude:float>,
                    <longitude:float>
                ]
        }
    },
]

This file converts the json file to python data dict.
"""
import json
from pathlib import Path

current_directory = BASE_DIR = Path(__file__).resolve().parent

with open(current_directory / "country_data.json") as country_file:
    COUNTRIES = json.load(country_file)
    COUNTRY_LIST = list(COUNTRIES.keys())
    COUNTRY_WITH_PROVINCE = {
        i: list(v["sub_divisions"].keys()) for i, v in COUNTRIES.items()
    }
    DIAL_CODES = ["+" + i["dial_code"] for i in COUNTRIES.values()]

    DIAL_CODE_NAME_MAP = {
        "+" + val["dial_code"]: "%s (+%s)" % (k, val["dial_code"])
        for k, val in COUNTRIES.items()
    }
    DIAL_CODES_WITH_NAME = list(DIAL_CODE_NAME_MAP.values())

with open(current_directory / "currencies.json") as currency_file:
    CURRENCIES = json.load(currency_file)
