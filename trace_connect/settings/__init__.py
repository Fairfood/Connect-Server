import os

from dotenv import load_dotenv


class Env:
    """Handle environment variables."""

    def __init__(self, **kwargs):
        """Load environment variables from .env file."""
        load_dotenv(**kwargs)

    def get(self, name, fallback=None):
        """Get environment variable or fallback to default value."""
        return os.environ.get(name, default=fallback)


env = Env(dotenv_path=".env")

settings_mapping = {
    "development": "development",
    "production": "production",
    "staging": "staging",
    "demo": "staging",  # same as staging
}

# Get the environment from the 'ENVIRONMENT' environment variable with a
# default of 'local'
settings_module = os.environ.get("ENVIRONMENT", "local")

print(f"Loading settings from 'trace_connect.settings.{settings_module}'...")

# Import the appropriate module based on the environment
from_module = settings_mapping.get(settings_module, "local")
exec(f"from .{from_module} import *")
