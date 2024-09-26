import re
import subprocess
import uuid
from datetime import timedelta

from base.exceptions.custom_exceptions import Conflict


def validate_semantic_version(version):
    """
    Regular expression for semantic versioning (e.g., 1.0.0, 2.3.4)
    """
    semver_regex = (
        r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-(alpha|beta|rc)\.\d+)?$"
    )

    if not re.match(semver_regex, version):
        raise ValueError(
            "Invalid semantic version. Use format MAJOR.MINOR.PATCH (e.g., 1.0.0)."
        )


def get_branch_name():
    """
    Get the name of the current Git branch.

    This method uses the 'subprocess' module to execute the 'git rev-parse --abbrev-ref HEAD' command,
    which returns the name of the current branch in the Git repository.

    Returns:
        str: The name of the current branch.

    Raises:
        subprocess.CalledProcessError: If there is an error executing the Git command.
    """
    try:
        branch_name = (
            subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            .strip()
            .decode("utf-8")
        )
        return branch_name
    except subprocess.CalledProcessError:
        raise Conflict("Failed to get the branch name.")


def get_server_version():
    """
    Retrieves the server version by extracting and formatting the branch name.
    Assumes the branch name follows a specific pattern like 'V1.0.0-staging'
    and removes unnecessary parts for versioning purposes.

    Returns:
        str: A cleaned server version string (e.g., '1.0.0').
    """

    # Get the current branch name (e.g., 'V1.0.0-staging')
    version = get_branch_name().replace("V", "")

    # Remove '-staging' from the version string (if present)
    version = version.replace("-staging", "")
    return version

