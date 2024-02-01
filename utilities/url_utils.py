"""Custom URL class for handling common operations on urls.

Domain validation is copied from the validators python library.
Ref :- https://github.com/kvesteri/validators/blob/master/validators/domain.py
"""
import re
from urllib.parse import urlencode

from django.utils.translation import gettext_lazy as _

domain_pattern = re.compile(
    r"^(?:[a-zA-Z0-9]"  # First character of the domain
    r"(?:[a-zA-Z0-9-_]{0,61}[A-Za-z0-9])?\.)"  # Sub domain + hostname
    r"+[A-Za-z0-9][A-Za-z0-9-_]{0,61}"  # First 61 characters of the gTLD
    r"[A-Za-z]$"  # Last character of the gTLD
)


def to_unicode(obj, charset="utf-8", errors="strict"):
    """Convert the input object to Unicode.

    If the input object is already a Unicode string, it is returned unchanged.
    If the input object is a bytes-like object, it is decoded using the
    specified character set and error handling strategy.

    Args:
        obj: The object to be converted to Unicode.
        charset (str, optional): The character set used for decoding bytes
            (default is "utf-8").
        errors (str, optional): The error handling strategy during decoding
            (default is "strict").

    Returns:
        Union[str, None]: The Unicode representation of the input object or
        None if the input is None.
    """
    if obj is None:
        return None
    if not isinstance(obj, bytes):
        return str(obj)
    return obj.decode(charset, errors)


class URL(str):
    """Represents a URL with convenient methods for building and manipulating
    it.

    This class is a subclass of str and extends it to provide additional
    functionality for working with URLs, including adding query parameters
    and building the full URL.

    Args:
        host (str): The host part of the URL.
        scheme (str, optional): The scheme of the URL (default is "https").

    Raises:
        ValueError: If an invalid host is provided.

    Attributes:
        full_url (str): The full URL including the scheme and host.
        query_params (dict): A dictionary representing the query parameters of
            the URL.
    """

    def __init__(self, host: str, scheme: str = "https"):
        """Initializes a new URL object with the given host and scheme.

        Args:
            host (str): The host part of the URL.
            scheme (str, optional): The scheme of the URL (default is "https").

        Raises:
            ValueError: If an invalid host is provided.
        """
        try:
            domain_pattern.match(
                to_unicode(host).encode("idna").decode("ascii")
            )
        except (UnicodeError, AttributeError):
            raise ValueError(_("Invalid host: %s") % host)
        self.full_url = host.strip("/")
        self.query_params = {}
        if "http" not in self.full_url:
            self.full_url = f"{scheme}://{self.full_url}"

    def __truediv__(self, value):
        """Implements the "/" operator to append a path segment to the URL.

        Args:
            value (str): The path segment to append.

        Returns:
            URL: A new URL object with the appended path segment.
        """
        value = value.strip("/")
        self.full_url = f"{self.full_url}/{value}"
        return self

    def __repr__(self):
        """Returns a string representation of the URL for debugging.

        Returns:
            str: A string representation of the URL.
        """
        return f"{self.full_url}?{urlencode(self.query_params)}"

    def __str__(self):
        """Returns a string representation of the URL.

        Returns:
            str: A string representation of the URL.
        """
        return f"{self.full_url}?{urlencode(self.query_params)}"

    def add_params(self, **kwargs):
        """Adds query parameters to the URL.

        Args:
            **kwargs: Keyword arguments representing query parameters.
        """
        self.query_params.update(**kwargs)
