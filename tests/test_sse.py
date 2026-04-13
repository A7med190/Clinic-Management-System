import pytest
from django.test import TestCase

from core.sse import SSEMixin, sse_stream_generator


class TestSSE(TestCase):
    def test_render_sse_event(self):
        class TestSSEView(SSEMixin):
            pass

        view = TestSSEView()
        result = view.render_sse_event("test_event", {"key": "value"})

        self.assertIn("event: test_event", result)
        self.assertIn('"key": "value"', result)

    def test_render_sse_event_with_string(self):
        class TestSSEView(SSEMixin):
            pass

        view = TestSSEView()
        result = view.render_sse_event("message", "plain text")

        self.assertIn("event: message", result)
        self.assertIn("plain text", result)

    def test_sse_stream_generator(self):
        events = [
            ("event1", {"data": "value1"}),
            ("event2", {"data": "value2"}),
        ]

        result = list(sse_stream_generator(events, heartbeat=False))

        self.assertEqual(len(result), 2)
        self.assertIn("event: event1", result[0])
        self.assertIn("event: event2", result[1])

    def test_sse_stream_generator_with_heartbeat(self):
        events = [("single", {"data": "value"})]

        result = list(sse_stream_generator(events, heartbeat=True))

        self.assertGreaterEqual(len(result), 1)
