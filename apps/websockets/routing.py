from django.urls import path

from apps.websockets.consumers import (
    AppointmentConsumer,
    BaseWebSocketConsumer,
    NotificationConsumer,
)

websocket_urlpatterns = [
    path("ws/", BaseWebSocketConsumer.as_asgi()),
    path("ws/notifications/", NotificationConsumer.as_asgi()),
    path("ws/appointments/", AppointmentConsumer.as_asgi()),
    path("ws/appointments/<str:appointment_id>/", AppointmentConsumer.as_asgi()),
]
