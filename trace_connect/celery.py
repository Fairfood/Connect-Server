"""Celery configurations are specified here."""
from __future__ import absolute_import
from __future__ import unicode_literals

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trace_connect.settings")

app = Celery("trace_connect")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.timezone = "UTC"
app.autodiscover_tasks()
