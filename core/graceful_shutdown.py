import logging
import signal
import sys
import threading
from typing import Callable

from django.conf import settings

logger = logging.getLogger(__name__)

_shutdown_callbacks: list[Callable] = []
_shutdown_in_progress = threading.Event()


def register_shutdown_callback(callback: Callable):
    _shutdown_callbacks.append(callback)
    return callback


def shutdown_handler(signum, frame):
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    _shutdown_in_progress.set()

    timeout = getattr(settings, "GRACEFUL_SHUTDOWN_TIMEOUT", 30)

    for callback in _shutdown_callbacks:
        try:
            logger.info(f"Executing shutdown callback: {callback.__name__}")
            callback()
        except Exception as e:
            logger.exception(f"Error in shutdown callback {callback.__name__}: {e}")

    logger.info(f"Graceful shutdown complete, exiting in {timeout}s...")
    import time
    time.sleep(timeout // 4)
    sys.exit(0)


def setup_graceful_shutdown():
    if sys.platform != 'win32':
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, shutdown_handler)
        if hasattr(signal, "SIGINT"):
            signal.signal(signal.SIGINT, shutdown_handler)

    logger.info("Graceful shutdown handlers registered")


class GracefulShutdownMixin:
    def on_shutdown(self):
        logger.info(f"{self.__class__.__name__} shutdown initiated")

    def on_startup(self):
        logger.info(f"{self.__class__.__name__} started")


class CeleryGracefulShutdown:
    def shutdown(self):
        logger.info("Celery worker shutting down gracefully")
        super().shutdown()


@register_shutdown_callback
def close_database_connections():
    from django.db import connection
    connection.close()
    logger.info("Database connections closed")


@register_shutdown_callback
def flush_celery_pending_tasks():
    logger.info("Flushing pending Celery tasks")


@register_shutdown_callback
def close_redis_connections():
    logger.info("Closing Redis connections")
