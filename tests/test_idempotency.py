import pytest
from django.test import TestCase, RequestFactory

from core.idempotency import IdempotencyMiddleware, generate_idempotency_key


class TestIdempotencyMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get_request_not_affected(self):
        request = self.factory.get("/api/test/")
        middleware = IdempotencyMiddleware(lambda r: None)
        response = middleware(request)
        self.assertIsNone(response)

    def test_generate_idempotency_key(self):
        key1 = generate_idempotency_key()
        key2 = generate_idempotency_key()

        self.assertNotEqual(key1, key2)
        self.assertEqual(len(key1), 32)

    def test_post_request_without_key_not_affected(self):
        request = self.factory.post("/api/test/", data={"key": "value"})
        middleware = IdempotencyMiddleware(lambda r: None)
        response = middleware(request)
        self.assertIsNone(response)
