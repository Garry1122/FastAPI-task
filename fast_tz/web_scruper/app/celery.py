import os

from celery import Celery
from celery.signals import setup_logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.local")

celery_app = Celery("scruppy")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.conf.broker_transport_options = {'visibility_timeout': 86400}
celery_app.autodiscover_tasks()


@setup_logging.connect
def config_loggers(*args, **kwargs):
    from logging.config import dictConfig
    from django.conf import settings
    dictConfig(settings.LOGGING)
