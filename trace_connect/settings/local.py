from .base import *  # noqa
from .base import ALLOWED_HOSTS
from .base import BASE_DIR
from .base import INSTALLED_APPS
from .base import MIDDLEWARE
from .base import REST_FRAMEWORK
from .base import SIMPLE_JWT
from .base import timedelta

DEBUG = True

ALLOWED_HOSTS += ["0.0.0.0", "localhost", "127.0.0.1"]
CSRF_TRUSTED_ORIGINS = ["http://localhost:8000"]
INSTALLED_APPS += [
    "drf_yasg",
]

STATIC_ROOT = BASE_DIR.parent / "app" / "static"

REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["anon"] = "500/min"

SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = timedelta(days=14)
SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"] = timedelta(days=14)

HUB_TOPIC_ID = "0.0.47654162"

PYINSTRUMENT_PROFILE_DIR = "profiles"
ENABLE_PROFILING = False
if ENABLE_PROFILING:
    MIDDLEWARE += ["pyinstrument.middleware.ProfilerMiddleware"]

AWS_DEFAULT_REGION = "eu-central-1"
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
