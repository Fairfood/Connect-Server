import pendulum
from django.utils.crypto import get_random_string


def formatter(fmt=""):
    """Function to generate random strings of a defined format.

    Example use as defaul for models
    from functools import partial
    ...
    code = models.CharField(
        max_length=500, null=True, blank=True,
        default=partial(formatter, "{Y}-{m}-{d}-{R10}"),
        verbose_name=_('Code'))

    Available options are,

    d   : Current day in dd format
    m   : Current month in mm format
    y   : Current year in yy format
    Y   : Current year in yyyy format
    r5  : 5 digit random alphanumeric string
    r10 : 10 digit random alphanumeric string
    R5  : 5 digit random capitalized alphanumeric string
    R10 : 10 digit random capitalized alphanumeric string
    """
    today = pendulum.today()
    variables = {
        "d": today.strftime("%d"),
        "m": today.strftime("%m"),
        "y": today.strftime("%y"),
        "Y": today.strftime("%Y"),
        "r5": get_random_string(5),
        "r10": get_random_string(10),
        "R5": get_random_string(5).upper(),
        "R10": get_random_string(10).upper(),
    }
    return fmt.format(**variables)
