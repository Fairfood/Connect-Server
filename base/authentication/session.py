from asgiref.local import Local

_active = Local()


def set_to_local(key, value):
    """Sets attribute to Thread Local Storage."""
    setattr(_active, key, value)
    return True


def get_from_local(key, default=None):
    """Gets attribute from Thread Local Storage."""
    return getattr(_active, key, default)
