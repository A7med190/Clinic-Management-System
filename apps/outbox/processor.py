import logging
from typing import TYPE_CHECKING

from django.conf import settings

if TYPE_CHECKING:
    from apps.outbox.models import OutboxMessage

logger = logging.getLogger(__name__)


class OutboxProcessor:
    def __init__(self, batch_size: int | None = None):
        self.batch_size = batch_size or getattr(
            settings, "OUTBOX_PROCESSOR_BATCH_SIZE", 100
        )

    def process_pending(self) -> int:
        from apps.outbox.models import OutboxMessage

        messages = OutboxMessage.objects.filter(
            status__in=["pending", "failed"],
            retry_count__lt=models.F("max_retries"),
        ).select_for_update(skip_locked=True)[: self.batch_size]

        processed = 0
        for message in messages:
            try:
                self._process_message(message)
                processed += 1
            except Exception as e:
                logger.exception(f"Failed to process outbox message {message.pk}")
                message.mark_failed(str(e))

        return processed

    def _process_message(self, message: "OutboxMessage"):
        logger.info(f"Processing outbox message: {message.event_type}")
        message.status = "processing"
        message.save(update_fields=["status"])
        message.mark_sent()
