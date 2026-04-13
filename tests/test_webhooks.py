import pytest
from django.test import TestCase

from apps.webhooks.models import WebhookSubscription, WebhookDelivery


class TestWebhookModels(TestCase):
    def test_create_subscription(self):
        subscription = WebhookSubscription.objects.create(
            url="https://example.com/webhook",
            event_types=["order.created", "order.updated"],
            secret="test_secret",
        )
        self.assertTrue(subscription.is_active)
        self.assertEqual(len(subscription.event_types), 2)

    def test_subscription_str(self):
        subscription = WebhookSubscription.objects.create(
            url="https://example.com/webhook",
            event_types=["event1", "event2"],
        )
        self.assertIn("example.com", str(subscription))

    def test_generate_signature(self):
        subscription = WebhookSubscription.objects.create(
            url="https://example.com/webhook",
            event_types=["test"],
            secret="secret_key",
        )
        signature = subscription.generate_signature("test_payload")
        self.assertNotEqual(signature, "")
        self.assertEqual(len(signature), 64)

    def test_generate_signature_no_secret(self):
        subscription = WebhookSubscription.objects.create(
            url="https://example.com/webhook",
            event_types=["test"],
        )
        signature = subscription.generate_signature("test_payload")
        self.assertEqual(signature, "")

    def test_create_delivery(self):
        subscription = WebhookSubscription.objects.create(
            url="https://example.com/webhook",
            event_types=["test"],
        )
        delivery = WebhookDelivery.objects.create(
            subscription=subscription,
            event_type="test.event",
            payload={"key": "value"},
        )
        self.assertEqual(delivery.status, "pending")
