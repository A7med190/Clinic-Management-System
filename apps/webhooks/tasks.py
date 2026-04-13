import logging
from typing import Any

from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def deliver_webhook_task(
    self,
    subscription_id: int,
    event_type: str,
    payload: dict[str, Any],
    object_id: int | None = None,
    content_type_id: int | None = None,
):
    from django.contrib.contenttypes.models import ContentType

    from apps.webhooks.models import WebhookDelivery, WebhookSubscription
    from apps.webhooks.utils import send_webhook

    try:
        subscription = WebhookSubscription.objects.get(pk=subscription_id)
    except WebhookSubscription.DoesNotExist:
        logger.warning(f"Subscription {subscription_id} not found")
        return

    if not subscription.is_active:
        logger.info(f"Subscription {subscription_id} is inactive")
        return

    delivery = WebhookDelivery.objects.create(
        subscription=subscription,
        event_type=event_type,
        payload=payload,
    )

    if object_id and content_type_id:
        delivery.object_id = object_id
        delivery.content_type_id = content_type_id
        delivery.save(update_fields=["object_id", "content_type_id"])

    webhook_payload = {
        "event": event_type,
        "data": payload,
        "timestamp": __import__("datetime").datetime.now().isoformat(),
    }

    timeout = getattr(settings, "WEBHOOK_DELIVERY_TIMEOUT", 30)
    success = send_webhook(
        subscription.url,
        webhook_payload,
        subscription.secret if subscription.secret else None,
        timeout,
    )

    if success:
        delivery.status = "success"
        delivery.delivered_at = __import__("django.utils.timezone").now()
        delivery.save(update_fields=["status", "delivered_at"])
    else:
        delivery.status = "failed"
        delivery.retry_count += 1
        delivery.save(update_fields=["status", "retry_count"])

        if self.request.retries < self.max_retries:
            retry_delays = getattr(settings, "WEBHOOK_RETRY_DELAYS", [60, 300, 900])
            delay = retry_delays[self.request.retries] if self.request.retries < len(retry_delays) else 60
            raise self.retry(exc=Exception("Webhook delivery failed"), countdown=delay)
