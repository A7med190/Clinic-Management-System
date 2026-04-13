import json
import logging
from typing import Any, AsyncIterator

from django.conf import settings
from django.http import HttpRequest, HttpResponse, StreamingHttpResponse

logger = logging.getLogger(__name__)


class SSEMixin:
    sse_heartbeat_interval: int = 30
    sse_retry_time: int = 5000

    def render_sse_event(self, event_type: str, data: Any) -> str:
        if isinstance(data, (dict, list)):
            content = json.dumps(data)
        else:
            content = str(data)

        return f"event: {event_type}\ndata: {content}\nretry: {self.sse_retry_time}\n\n"

    def sse_response(
        self, request: HttpRequest, event_generator: callable
    ) -> StreamingHttpResponse:
        response = StreamingHttpResponse(
            streaming_content=event_generator(request),
            content_type="text/event-stream",
        )
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response


class SSEConsumer:
    def __init__(self):
        self.clients: dict[str, list] = {}

    def add_client(self, group: str, callback: callable):
        if group not in self.clients:
            self.clients[group] = []
        self.clients[group].append(callback)

    def remove_client(self, group: str, callback: callable):
        if group in self.clients and callback in self.clients[group]:
            self.clients[group].remove(callback)

    def broadcast(self, group: str, event_type: str, data: Any):
        if group not in self.clients:
            return

        message = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"

        for callback in self.clients[group]:
            try:
                callback(message)
            except Exception as e:
                logger.exception(f"Error broadcasting to client: {e}")


class SSEView(SSEMixin):
    def get(self, request: HttpRequest, **kwargs) -> HttpResponse:
        return self.sse_response(request, self.event_stream)

    def event_stream(self, request: HttpRequest):
        import time

        heartbeat_interval = getattr(settings, "SSE_HEARTBEAT_INTERVAL", 30)
        last_heartbeat = time.time()

        while True:
            if time.time() - last_heartbeat >= heartbeat_interval:
                yield ": heartbeat\n\n"
                last_heartbeat = time.time()

            time.sleep(1)


def sse_stream_generator(
    events: list[tuple[str, dict]],
    heartbeat: bool = True,
) -> AsyncIterator[str]:
    import time

    last_heartbeat = time.time()
    heartbeat_interval = getattr(settings, "SSE_HEARTBEAT_INTERVAL", 30)

    for event_type, data in events:
        yield f"event: {event_type}\ndata: {json.dumps(data)}\n\n"

        if heartbeat and time.time() - last_heartbeat >= heartbeat_interval:
            yield ": heartbeat\n\n"
            last_heartbeat = time.time()
