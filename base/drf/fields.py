import decimal

from django.utils.encoding import smart_str
from django.utils.formats import sanitize_separators
from hashid_field.field import Hashid
from phonenumber_field.phonenumber import PhoneNumber
from phonenumber_field.serializerfields import PhoneNumberField
from phonenumbers import NumberParseException
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from utilities.functions import unix_to_datetime


class UnixDateTimeField(serializers.DateTimeField):
    """A custom field to accept Unix timestamps in a DateTimeField.

    This field extends `serializers.DateTimeField` to enable the use of Unix
    timestamps, which are represented as integers representing the number of
    seconds since the Unix epoch (January 1, 1970, 00:00:00 UTC).

    Usage:
        If you want to include this field in a serializer, you should add it as
        a class attribute, like this:
        ```
        class MySerializer(serializers.ModelSerializer):
            unix_datetime = UnixDateTimeField()
            ...
        ```
    """

    def to_internal_value(self, data):
        """Converts a Unix timestamp to a Python datetime object.

        Args:
            data (int): The Unix timestamp to convert.

        Returns:
            datetime: The corresponding Python datetime object.
        """
        # delegate conversion to a separate function
        return unix_to_datetime(data)


class RemovableImageField(serializers.ImageField, serializers.CharField):
    """A field that allows the removal of an existing image by passing an empty
    value.

    This field extends both `serializers.ImageField` and
    `serializers.CharField` to enable the removal of images, since empty values
    are not accepted by the `ImageField`. However, if an empty value is passed
    for the field in a serializer update, the image ID is correctly removed.

    Note:
        If you want to include this field in a serializer, you should add it as
        a class attribute, like this:
        ```
        class MySerializer(serializers.ModelSerializer):
            image = RemovableImageField()
            ...
        ```
    """

    def to_internal_value(self, data):
        """Returns an empty string if the input is an empty string, or
        delegates to the base `to_internal_value` method otherwise.

        Args:
            data (str): The input data to be parsed.

        Returns:
            str: An empty string if the input is an empty string, or the
            internal value returned by the base method.
        """
        if not data:
            # if input is empty, return an empty string
            return data
        # delegate to the base `to_internal_value` method otherwise
        return super(serializers.ImageField, self).to_internal_value(data)


class RoundingDecimalField(serializers.DecimalField):
    """A decimal field that will automatically round to the specified number of
    decimal places.

    Args:
        decimal_places (int): The number of decimal places to round to.
    """

    @staticmethod
    def round_decimal(value, places):
        """Rounds a decimal value to the specified number of decimal places.

        Args:
            value (decimal.Decimal): The decimal value to be rounded.
            places (int): The number of decimal places to round to.

        Returns:
            decimal.Decimal: The rounded decimal value.
        """
        if value is not None:
            # see
            # https://docs.python.org/2/library/decimal.html#decimal.Decimal.
            # quantize  for options
            return value.quantize(decimal.Decimal(10) ** -places)
        return value

    def to_internal_value(self, data):
        """Parses the input data and returns the validated and rounded decimal
        value.

        Args:
            data (str): The input data to be parsed.

        Returns:
            decimal.Decimal: The validated and rounded decimal value.

        Raises:
            serializers.ValidationError: if the input data is invalid or
            exceeds the maximum length.
        """
        data = smart_str(data).strip()

        if self.localize:
            data = sanitize_separators(data)

        if len(data) > self.MAX_STRING_LENGTH:
            # raises a ValidationError if the input data exceeds the maximum
            # length
            self.fail("max_string_length")

        try:
            value = decimal.Decimal(data)
        except decimal.DecimalException:
            # raises a ValidationError if the input data is invalid
            self.fail("invalid")

        # Check for NaN. It is the only value that isn't equal to itself,
        # so we can use this to identify NaN values.
        if value != value:
            # raises a ValidationError if the input data is NaN
            self.fail("invalid")

        # Check for infinity and negative infinity.
        if value in (decimal.Decimal("Inf"), decimal.Decimal("-Inf")):
            # raises a ValidationError if the input data is infinity or
            # negative infinity
            self.fail("invalid")

        value = self.round_decimal(value, self.decimal_places)

        return self.quantize(self.validate_precision(value))


class SerializableRelatedField(serializers.PrimaryKeyRelatedField):
    """A custom related field that can serialize related objects using a
    specified serializer."""

    def __init__(self, serializer=None, **kwargs):
        """Initializes the field with a specified serializer.

        Args:
            serializer: The serializer to use for serializing related objects.
            kwargs: Additional keyword arguments to pass to the base class.
        """
        self.serializer = serializer
        self.many = kwargs.get("many", False)
        super().__init__(**kwargs)

    def use_pk_only_optimization(self):
        """Disable the primary key optimization.

        By default, this field uses primary key optimization, which may not be
        suitable for custom serialization. So, we disable it here.

        Returns:
            False to disable primary key optimization.
        """
        return False

    def single_to_representation(self, value):
        """Convert a single related object to its serialized representation.

        Args:
            value: The related object to serialize.

        Returns:
            The serialized representation of the related object.
        """

        if not value:
            return None
        if isinstance(value, Hashid):
            return value
        return value.pk

    def to_representation(self, value):
        """Serializes the related object using the specified serializer.

        If no serializer is specified, delegates to the base class
        implementation.

        Args:
            value: The related object to serialize.

        Returns:
            The serialized representation of the related object.
        """
        if self.serializer is not None:
            return self.serializer(value, many=self.many).data
        if self.many:
            return [self.single_to_representation(obj) for obj in value]
        return self.single_to_representation(value)
        # return super().to_representation(value)


class PhoneNumberField(PhoneNumberField):
    """A custom field to accept phone numbers in a PhoneNumberField.

    This field extends the PhoneNumberField and provides additional
    functionality for handling phone numbers.
    """

    def to_internal_value(self, data):
        """Convert the external representation of data to the internal value.

        Args:
            data: The external representation of the data.

        Returns:
            object: The internal representation of the data.
        """
        try:
            return super().to_internal_value(data)
        except ValidationError:
            return None

    def to_representation(self, value):
        """Convert the internal value of the field to its external
        representation.

        Args:
            value: The internal representation of the data.

        Returns:
            str: The external representation of the data.
        """
        if value:
            if isinstance(value, str):
                try:
                    value = PhoneNumber.from_string(value)
                except NumberParseException:
                    return None
            return value.as_international
        return None
