import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def log_webhook_delivery(
    event_type: str,
    url: str,
    success: bool,
    status_code: int | str | None = None,
    error: str | None = None,
):
    from apps.webhooks.models import WebhookSubscription

    level = logging.INFO if success else logging.ERROR
    message = f"Webhook delivery - {event_type} to {url}"
    if success:
        message += f" - Status: {status_code}"
    else:
        message += f" - Error: {error or status_code}"

    logger.log(level, message)

    try:
        subscription = WebhookSubscription.objects.filter(url=url).first()
        if subscription:
            if success:
                subscription.failure_count = 0
                subscription.last_triggered_at = __import__("django.utils.timezone").now()
            else:
                subscription.failure_count += 1
                if subscription.failure_count >= 5:
                    subscription.is_active = False
            subscription.save(update_fields=["failure_count", "last_triggered_at", "is_active"])
    except Exception:
        pass


def send_webhook(url: str, payload: dict, secret: str | None = None, timeout: int = 30) -> bool:
    import json
    import hashlib
    import hmac

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "ClinicManagementSystem/1.0",
    }

    json_payload = json.dumps(payload)
    if secret:
        signature = hmac.new(secret.encode(), json_payload.encode(), hashlib.sha256).hexdigest()
        headers["X-Webhook-Signature"] = signature

    try:
        response = requests.post(url, data=json_payload, headers=headers, timeout=timeout)
        return 200 <= response.status_code < 300
    except requests.RequestException as e:
        logger.error(f"Webhook request failed: {e}")
        return False
