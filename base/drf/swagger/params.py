from drf_yasg import openapi


def add_query_params(*args):
    """Function takes in list of parameters as args and return
    openapi.Parameter objects as list."""
    return [
        openapi.Parameter(
            param,
            openapi.IN_QUERY,
            description=" ".join(param.split("_")).title(),
            type=openapi.IN_QUERY,
        )
        for param in args
    ]
