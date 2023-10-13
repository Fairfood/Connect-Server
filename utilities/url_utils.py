"""
Custom URL class for handling common operations on urls.
Domain validation is copied from the validators python library.
Ref :- https://github.com/kvesteri/validators/blob/master/validators/domain.py
"""
import re
from urllib.parse import urlencode
from django.utils.translation import gettext_lazy as _

domain_pattern = re.compile(
    r'^(?:[a-zA-Z0-9]'  # First character of the domain
    r'(?:[a-zA-Z0-9-_]{0,61}[A-Za-z0-9])?\.)'  # Sub domain + hostname
    r'+[A-Za-z0-9][A-Za-z0-9-_]{0,61}'  # First 61 characters of the gTLD
    r'[A-Za-z]$'  # Last character of the gTLD
)


def to_unicode(obj, charset='utf-8', errors='strict'):
    if obj is None:
        return None
    if not isinstance(obj, bytes):
        return str(obj)
    return obj.decode(charset, errors)


class URL(str):

    def __init__(self, host: str, scheme: str = 'https'):
        try:
            domain_pattern.match(to_unicode(host).encode('idna').decode('ascii'))
        except (UnicodeError, AttributeError):
            raise ValueError(_("Invalid host: %s") % host)
        self.full_url = host.strip('/')
        self.query_params = {}
        if 'http' not in self.full_url:
            self.full_url = f"{scheme}://{self.full_url}"

    def __truediv__(self, value):
        value = value.strip('/')
        self.full_url = f"{self.full_url}/{value}"
        return self

    def __repr__(self):
        return f"{self.full_url}?{urlencode(self.query_params)}"

    def __str__(self):
        return f"{self.full_url}?{urlencode(self.query_params)}"

    def add_params(self, **kwargs):
        self.query_params.update(**kwargs)
