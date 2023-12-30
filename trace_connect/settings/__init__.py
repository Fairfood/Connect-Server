import os

from dotenv import load_dotenv


# Load the .env file
load_dotenv()

# Get the environment variables
env = os.environ

settings_mapping = {
    "development": "development",
    "production": "production",
    "staging": "staging",
    "demo": "staging",  # same as staging
}

# Get the environment from the 'ENVIRONMENT' environment variable with a
# default of 'local'
settings_module = env.get("ENVIRONMENT", "local")


# Import the appropriate module based on the environment
from_module = settings_mapping.get(settings_module, "local")
exec(f"from .{from_module} import *")
