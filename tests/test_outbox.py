import pytest
from django.test import TestCase, override_settings

from apps.outbox.models import OutboxMessage, publish_outbox_event


class TestOutbox(TestCase):
    def test_create_outbox_message(self):
        message = OutboxMessage.objects.create(
            event_type="test.event",
            payload={"key": "value"},
        )
        self.assertEqual(message.status, "pending")
        self.assertEqual(message.event_type, "test.event")

    def test_mark_sent(self):
        message = OutboxMessage.objects.create(
            event_type="test.event",
            payload={"key": "value"},
        )
        message.mark_sent()
        message.refresh_from_db()
        self.assertEqual(message.status, "sent")
        self.assertIsNotNone(message.processed_at)

    def test_mark_failed(self):
        message = OutboxMessage.objects.create(
            event_type="test.event",
            payload={"key": "value"},
        )
        message.mark_failed("Test error")
        message.refresh_from_db()
        self.assertEqual(message.retry_count, 1)
        self.assertEqual(message.error_message, "Test error")

    def test_mark_failed_max_retries(self):
        message = OutboxMessage.objects.create(
            event_type="test.event",
            payload={"key": "value"},
            max_retries=3,
            retry_count=2,
        )
        message.mark_failed("Final error")
        message.refresh_from_db()
        self.assertEqual(message.status, "failed")

    def test_publish_outbox_event(self):
        event_type = "custom.event"
        payload = {"data": "test"}

        publish_outbox_event(event_type, payload)

        message = OutboxMessage.objects.filter(event_type=event_type).first()
        self.assertIsNotNone(message)
        self.assertEqual(message.payload, payload)
