import pytest
from django.test import TestCase

from core.circuit_breaker import circuit_breaker, get_circuit_breaker


class TestCircuitBreaker(TestCase):
    def test_get_circuit_breaker_creates_new(self):
        breaker = get_circuit_breaker("test_circuit")
        self.assertIsNotNone(breaker)

    def test_get_circuit_breaker_returns_same_instance(self):
        breaker1 = get_circuit_breaker("same_circuit")
        breaker2 = get_circuit_breaker("same_circuit")
        self.assertIs(breaker1, breaker2)

    def test_circuit_breaker_decorator(self):
        call_count = {"count": 0}

        @circuit_breaker("decorator_test", fail_max=3, reset_timeout=60)
        def test_function():
            call_count["count"] += 1
            return "success"

        result = test_function()
        self.assertEqual(result, "success")
        self.assertEqual(call_count["count"], 1)

    def test_circuit_breaker_fallback(self):
        fallback_called = {"called": False}

        def fallback():
            fallback_called["called"] = True
            return "fallback_result"

        @circuit_breaker("fallback_test", fallback=fallback, fail_max=1, reset_timeout=60)
        def failing_function():
            raise Exception("Test exception")

        with self.assertRaises(Exception):
            failing_function()

        self.assertTrue(fallback_called["called"])
