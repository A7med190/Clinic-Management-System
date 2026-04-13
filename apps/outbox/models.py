import json
import logging
from datetime import datetime
from typing import Any

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)


class OutboxMessage(models.Model):
    event_type = models.CharField(max_length=255)
    payload = models.JSONField()
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("sent", "Sent"),
            ("failed", "Failed"),
        ],
        default="pending",
    )
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    scheduled_at = models.DateTimeField(blank=True, null=True)

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
            models.Index(fields=["status", "scheduled_at"]),
            models.Index(fields=["event_type", "status"]),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.status}"

    def mark_sent(self):
        self.status = "sent"
        self.processed_at = timezone.now()
        self.save(update_fields=["status", "processed_at"])

    def mark_failed(self, error: str):
        self.retry_count += 1
        if self.retry_count >= self.max_retries:
            self.status = "failed"
        self.error_message = error
        self.save(update_fields=["status", "retry_count", "error_message"])


class OutboxableMixin(models.Model):
    outbox_messages = GenericRelation(OutboxMessage, related_query_name="%(class)s")

    class Meta:
        abstract = True

    def publish_event(self, event_type: str, payload: dict[str, Any] | None = None):
        if payload is None:
            payload = self._get_event_payload()

        OutboxMessage.objects.create(
            event_type=event_type,
            payload=payload,
            content_object=self,
        )

    def _get_event_payload(self) -> dict[str, Any]:
        return {
            "model": self.__class__.__name__,
            "pk": self.pk,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def publish_outbox_event(
    event_type: str,
    payload: dict[str, Any],
    obj: models.Model | None = None,
    scheduled_at: datetime | None = None,
):
    if obj and isinstance(obj, OutboxableMixin):
        obj.publish_event(event_type, payload)
    else:
        message = OutboxMessage.objects.create(
            event_type=event_type,
            payload=payload,
        )
        if obj:
            message.content_object = obj
            message.save(update_fields=["content_type", "object_id"])
        if scheduled_at:
            message.scheduled_at = scheduled_at
            message.save(update_fields=["scheduled_at"])
