import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.sender = self.scope["user"]

        if not self.sender.is_authenticated:
            await self.close()
            return

        # Static room name since URL has no room_name param
        self.room_name = 'global'
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "")
        image = data.get("image", "")

        # Save message
        await self.save_message(self.sender, message, image)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": self.sender.username,
                "image": image
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "image": event.get("image", "")
        }))

    @database_sync_to_async
    def save_message(self, sender, content, image):
        return Message.objects.create(
            sender=sender,
            recipient=None,
            content=content,
            image=image
        )
