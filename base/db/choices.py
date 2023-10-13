import enum
from django.db.models.enums import Choices, ChoicesMeta


class CallableChoicesMeta(ChoicesMeta):
    """
    A metaclass for creating a callable enum choices.
    """

    def __new__(metacls, classname, bases, classdict, **kwds):
        labels = []
        functions = []
        for key in classdict._member_names:
            value = classdict[key]
            value, function, label = value
            labels.append(label)
            functions.append(function)
            # Use dict.__setitem__() to suppress defenses against double
            # assignment in enum's classdict.
            dict.__setitem__(classdict, key, value)
        cls = super().__new__(metacls, classname, bases, classdict, **kwds)
        for member, label in zip(cls.__members__.values(), labels):
            member._label_ = label
        for member, function in zip(cls.__members__.values(), functions):
            member._function_ = function
        return enum.unique(cls)


class CallableChoices(Choices, metaclass=CallableChoicesMeta):
    """Class for creating enumerated choices."""

    def function(self, *args, **kwargs):
        return self._function_(*args, **kwargs)


class CallableIntegerChoices(int, CallableChoices):
    """Class for creating enumerated callable integer choices."""

    pass


class CallableTextChoices(str, CallableChoices):
    """Class for creating enumerated callable string choices."""

    def _generate_next_value_(name, start, count, last_values):
        return name
