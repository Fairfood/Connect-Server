from django.utils.crypto import get_random_string


def get_file_path(instance, filename):
    """
    Function to get filepath for a file to be uploaded
    Args:
        instance: instance of the file object
        filename: uploaded filename

    Returns:
        path: Path of file
    """
    type = instance.__class__.__name__.lower()
    path = "%s/%s_%s:%s" % (
        type,
        instance.id.id,
        get_random_string(10),
        filename,
    )
    return path
