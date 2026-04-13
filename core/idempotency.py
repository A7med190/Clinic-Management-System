import hashlib
import logging
import time
import uuid
from typing import Callable

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


class IdempotencyMiddleware:
    def __init__(self, get_response: Callable):
        self.get_response = get_response
        self.header_name = getattr(settings, "IDEMPOTENCY_HEADER", "HTTP_X_IDEMPOTENCY_KEY")
        self.cache_prefix = getattr(settings, "IDEMPOTENCY_CACHE_PREFIX", "idempotency:")
        self.cache_timeout = getattr(settings, "IDEMPOTENCY_CACHE_TIMEOUT", 86400)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
            return self.get_response(request)

        idempotency_key = request.headers.get("X-Idempotency-Key")

        if not idempotency_key:
            return self.get_response(request)

        if request.method == "POST" and "/api/" in request.path:
            return self._handle_idempotent_request(request, idempotency_key)

        return self.get_response(request)

    def _handle_idempotent_request(self, request: HttpRequest, idempotency_key: str) -> HttpResponse:
        cache_key = f"{self.cache_prefix}{idempotency_key}"

        cached_response = cache.get(cache_key)
        if cached_response:
            logger.info(f"Returning cached response for idempotency key: {idempotency_key}")
            response = HttpResponse(
                content=cached_response["content"],
                status=cached_response["status"],
                content_type=cached_response.get("content_type", "application/json"),
            )
            response["X-Idempotent-Replay"] = "true"
            return response

        request.idempotency_key = idempotency_key
        response = self.get_response(request)

        if 200 <= response.status_code < 300:
            cache.set(
                cache_key,
                {
                    "content": response.content.decode("utf-8"),
                    "status": response.status_code,
                    "content_type": response.get("Content-Type", ""),
                },
                self.cache_timeout,
            )

        return response


def generate_idempotency_key() -> str:
    return uuid.uuid4().hex


class IdempotentRequestMixin:
    idempotency_key_field: str = "idempotency_key"

    def get_idempotency_key(self) -> str | None:
        key = getattr(settings, "IDEMPOTENCY_HEADER", "HTTP_X_IDEMPOTENCY_KEY")
        key_name = key.replace("HTTP_", "").replace("_", "-")
        return self.request.headers.get(f"X-Idempotency-Key")

    def cache_response(self, response_data: dict, key: str):
        cache_key = f"idempotency:{key}"
        cache.set(cache_key, response_data, timeout=86400)

    def get_cached_response(self, key: str) -> dict | None:
        cache_key = f"idempotency:{key}"
        return cache.get(cache_key)
