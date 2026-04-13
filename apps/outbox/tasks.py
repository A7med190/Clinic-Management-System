from celery import shared_task

from apps.outbox.processor import OutboxProcessor


@shared_task
def process_outbox_task():
    processor = OutboxProcessor()
    processed = processor.process_pending()
    return f"Processed {processed} outbox messages"
