import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class BaseWebSocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = self.scope.get("url_route", {}).get("kwargs", {}).get(
            "room_name", "default"
        )
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        logger.info(f"WebSocket connected: {self.channel_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.info(f"WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data) if text_data else {}
            await self.handle_message(data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Invalid JSON"}))
        except Exception as e:
            logger.exception("Error processing WebSocket message")
            await self.send(text_data=json.dumps({"error": str(e)}))

    async def handle_message(self, data: dict):
        await self.send(text_data=json.dumps({"type": "echo", "data": data}))

    async def broadcast_message(self, event: dict):
        await self.send(text_data=json.dumps(event))


class NotificationConsumer(BaseWebSocketConsumer):
    async def connect(self):
        await super().connect()
        await self.channel_layer.group_add("notifications", self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notifications", self.channel_name)
        await super().disconnect(close_code)

    async def notification_message(self, event: dict):
        await self.send(text_data=json.dumps(event["message"]))


class AppointmentConsumer(BaseWebSocketConsumer):
    async def connect(self):
        self.appointment_id = self.scope["url_route"]["kwargs"].get("appointment_id")
        group_name = f"appointment_{self.appointment_id}" if self.appointment_id else "appointments"
        
        await self.channel_layer.group_add(group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        group_name = f"appointment_{self.appointment_id}" if self.appointment_id else "appointments"
        await self.channel_layer.group_discard(group_name, self.channel_name)
        await super().disconnect(close_code)

    async def appointment_update(self, event: dict):
        await self.send(text_data=json.dumps(event["data"]))
