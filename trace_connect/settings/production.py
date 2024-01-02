import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .base import *  # noqa
from .base import DEPLOYMENT
from .base import env
from .base import REST_FRAMEWORK

ENVIRONMENT = "production"
DEBUG = False

ALLOWED_HOSTS = [
    "v2.api.fairfood.org",
]

CORS_ORIGIN_WHITELIST = ("https://v2.api.fairfood.org",)

REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["anon"] = "5/min"

HEDERA_NETWORK = 3  # For Mainnet

AWS_DEFAULT_REGION = "eu-central-1"
AWS_ACCESS_KEY_ID = env.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env.get("AWS_STORAGE_BUCKET_NAME")
AWS_QUERYSTRING_AUTH = False
AWS_PRELOAD_METADATA = True
AWS_DEFAULT_ACL = "public-read"
DEFAULT_FILE_STORAGE = "s3_folder_storage.s3.DefaultStorage"
DEFAULT_S3_PATH = "media"
MEDIA_ROOT = "/%s/" % DEFAULT_S3_PATH
MEDIA_URL = "//%s.s3.amazonaws.com/media/" % AWS_STORAGE_BUCKET_NAME

sentry_sdk.init(
    dsn=env.get("SENTRY_DSN"),
    integrations=[
        DjangoIntegration(),
        CeleryIntegration(),
        RedisIntegration(),
    ],
    traces_sample_rate=1.0,
    environment=ENVIRONMENT,
)
sentry_sdk.set_tag("deployment", DEPLOYMENT)

# SWAGGER_SETTINGS = {}
