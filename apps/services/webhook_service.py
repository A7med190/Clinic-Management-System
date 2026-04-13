from abc import abstractmethod
from typing import Any

import requests
from django.conf import settings
from django.core.cache import cache
from pybreaker import CircuitBreaker, CircuitBreakerError

from apps.webhooks.utils import log_webhook_delivery


class WebhookService:
    def __init__(self):
        self.timeout = getattr(settings, "WEBHOOK_DELIVERY_TIMEOUT", 30)
        self.max_retries = getattr(settings, "WEBHOOK_MAX_RETRIES", 3)
        self.circuit_breaker = self._setup_circuit_breaker()

    def _setup_circuit_breaker(self) -> CircuitBreaker:
        cb_settings = getattr(settings, "CIRCUIT_BREAKER", {})
        return CircuitBreaker(
            fail_max=cb_settings.get("FAILURE_THRESHOLD", 5),
            reset_timeout=cb_settings.get("RECOVERY_TIMEOUT", 60),
        )

    def send(
        self,
        url: str,
        payload: dict[str, Any],
        headers: dict[str, str] | None = None,
        event_type: str = "webhook",
    ) -> tuple[bool, dict[str, Any]]:
        default_headers = {
            "Content-Type": "application/json",
            "User-Agent": "ClinicManagementSystem/1.0",
        }
        if headers:
            default_headers.update(headers)

        try:
            response = self.circuit_breaker.call(
                requests.post,
                url,
                json=payload,
                headers=default_headers,
                timeout=self.timeout,
            )
            success = 200 <= response.status_code < 300
            log_webhook_delivery(event_type, url, success, response.status_code)
            return success, {"status_code": response.status_code, "body": response.text}
        except CircuitBreakerError:
            logger = __import__("logging").getLogger(__name__)
            logger.warning(f"Circuit breaker open for URL: {url}")
            return False, {"error": "Circuit breaker open"}
        except requests.RequestException as e:
            log_webhook_delivery(event_type, url, False, error=str(e))
            return False, {"error": str(e)}


class WebhookSubscriptionService:
    def subscribe(self, url: str, event_types: list[str], secret: str | None = None):
        from apps.webhooks.models import WebhookSubscription

        subscription, created = WebhookSubscription.objects.get_or_create(
            url=url,
            defaults={"event_types": event_types, "secret": secret or ""},
        )
        if not created:
            subscription.event_types = event_types
            if secret:
                subscription.secret = secret
            subscription.is_active = True
            subscription.save()
        return subscription

    def unsubscribe(self, url: str):
        from apps.webhooks.models import WebhookSubscription

        WebhookSubscription.objects.filter(url=url).update(is_active=False)

    def get_subscriptions(self, event_type: str):
        from apps.webhooks.models import WebhookSubscription

        return WebhookSubscription.objects.filter(
            is_active=True, event_types__contains=[event_type]
        )
