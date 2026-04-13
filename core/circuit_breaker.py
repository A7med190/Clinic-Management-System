import functools
import logging
import time
from typing import Any, Callable

from django.conf import settings
from django.core.cache import cache
from pybreaker import CircuitBreaker, CircuitBreakerError

logger = logging.getLogger(__name__)

_circuit_breakers: dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str) -> CircuitBreaker:
    if name not in _circuit_breakers:
        cb_settings = getattr(settings, "CIRCUIT_BREAKER", {})
        _circuit_breakers[name] = CircuitBreaker(
            fail_max=cb_settings.get("FAILURE_THRESHOLD", 5),
            reset_timeout=cb_settings.get("RECOVERY_TIMEOUT", 60),
        )
    return _circuit_breakers[name]


def circuit_breaker(
    name: str,
    fallback: Callable[..., Any] | None = None,
    exclude_exceptions: tuple = (),
):
    def decorator(func: Callable) -> Callable:
        breaker = get_circuit_breaker(name)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return breaker.call(func, *args, **kwargs)
            except CircuitBreakerError:
                logger.warning(f"Circuit breaker '{name}' is open for {func.__name__}")
                if fallback:
                    return fallback(*args, **kwargs)
                raise
            except exclude_exceptions:
                return func(*args, **kwargs)

        wrapper.circuit_breaker = breaker
        return wrapper

    return decorator


class CircuitBreakerMixin:
    circuit_breaker_name: str = ""

    def get_circuit_breaker(self) -> CircuitBreaker:
        if not self.circuit_breaker_name:
            raise ValueError("circuit_breaker_name must be defined")
        return get_circuit_breaker(self.circuit_breaker_name)

    def call_with_circuit_breaker(self, func: Callable, *args, **kwargs):
        breaker = self.get_circuit_breaker()
        try:
            return breaker.call(func, *args, **kwargs)
        except CircuitBreakerError:
            logger.warning(f"Circuit breaker '{self.circuit_breaker_name}' is open")
            raise
