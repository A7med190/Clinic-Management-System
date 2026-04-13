import hashlib
import hmac
import json
import logging
from datetime import datetime

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

logger = logging.getLogger(__name__)


class WebhookSubscription(models.Model):
    url = models.URLField(max_length=2048)
    event_types = models.JSONField(default=list)
    secret = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_triggered_at = models.DateTimeField(blank=True, null=True)
    failure_count = models.IntegerField(default=0)

    class Meta:
        db_table = "webhook_subscriptions"
        unique_together = [["url"]]

    def __str__(self):
        return f"{self.url} ({', '.join(self.event_types)})"

    def generate_signature(self, payload: str) -> str:
        if not self.secret:
            return ""
        return hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()


class WebhookDelivery(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("retrying", "Retrying"),
    ]

    subscription = models.ForeignKey(
        WebhookSubscription,
        on_delete=models.CASCADE,
        related_name="deliveries",
    )
    event_type = models.CharField(max_length=255)
    payload = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    status_code = models.IntegerField(blank=True, null=True)
    response_body = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(blank=True, null=True)

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.status}"


class WebhookableMixin(models.Model):
    webhooks = GenericRelation(WebhookDelivery)

    class Meta:
        abstract = True

    def trigger_webhook(self, event_type: str, payload: dict | None = None):
        from apps.webhooks.tasks import deliver_webhook_task

        if payload is None:
            payload = {
                "model": self.__class__.__name__,
                "pk": self.pk,
                "timestamp": datetime.now().isoformat(),
            }

        subscriptions = WebhookSubscription.objects.filter(
            is_active=True, event_types__contains=[event_type]
        )

        for subscription in subscriptions:
            deliver_webhook_task.delay(
                subscription_id=subscription.pk,
                event_type=event_type,
                payload=payload,
                object_id=self.pk,
                content_type_id=ContentType.objects.get_for_model(self).pk,
            )
