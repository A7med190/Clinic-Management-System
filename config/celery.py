import os
import signal

from celery import Celery
from celery.signals import worker_shutdown, worker_init

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@worker_init.connect
def on_worker_init(**kwargs):
    import logging
    logging.getLogger(__name__).info("Celery worker initialized")


@worker_shutdown.connect
def on_worker_shutdown(**kwargs):
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Celery worker shutting down gracefully")
    from django.db import connection
    connection.close()
    logger.info("Database connections closed during shutdown")
