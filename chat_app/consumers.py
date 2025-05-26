import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    active_users = set()  

    async def connect(self):
        self.sender = self.scope["user"]

        if not self.sender.is_authenticated:
            await self.close()
            return

        self.username = self.sender.username
        self.room_name = 'global'
        self.room_group_name = f'chat_{self.room_name}'

        ChatConsumer.active_users.add(self.username)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        await self.send_user_list()

    async def disconnect(self, close_code):
        ChatConsumer.active_users.discard(self.username)

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.send_user_list()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message")
        image = data.get("image")
        typing = data.get("typing")

        if typing:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_typing",
                    "sender": self.username
                }
            )
        elif message or image:
            await self.save_message(self.sender, message or "", image or "")
            avatar_url = await self.get_avatar_url_with_cache_buster(self.sender)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message or "",
                    "sender": self.username,
                    "image": image or "",
                    "avatar": avatar_url
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "image": event.get("image", ""),
            "avatar": event.get("avatar", "/static/default-avatar.png")
        }))

    async def user_typing(self, event):
        await self.send(text_data=json.dumps({
            "typing": True,
            "sender": event["sender"]
        }))

    async def send_user_list(self):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_list",
                "users": list(ChatConsumer.active_users)
            }
        )

    async def user_list(self, event):
        await self.send(text_data=json.dumps({
            "users": event["users"]
        }))

    @database_sync_to_async
    def save_message(self, sender, content, image):
        return Message.objects.create(
            sender=sender,
            recipient=None,
            content=content,
            image=image
        )
    
    @database_sync_to_async
    def get_avatar_url_with_cache_buster(self, user):
        profile = user.profile
        avatar_url = profile.avatar.url
        timestamp = int(profile.avatar_updated_at.timestamp())
        return f"{avatar_url}?{timestamp}"
