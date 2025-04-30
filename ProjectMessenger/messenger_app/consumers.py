import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile
from django.utils import timezone
from asgiref.sync import async_to_sync, sync_to_async

from .models import Message, ChatRoom, CustomUser

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'

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
        message_text = data.get('message')
        username = data.get('username')
        image_data = data.get('image')

        user = await self.get_user(username)
        chat = await self.get_chat(self.chat_id)

        msg = Message(chat=chat, sender=user, text=message_text)

        if image_data:
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            file_name = f"image_{user.id}_{timezone.now().timestamp()}.{ext}"
            await sync_to_async(msg.image.save)(file_name, ContentFile(base64.b64decode(imgstr)), save=True)
        else:
            await sync_to_async(msg.save)()

        print("Message received in consumer")

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_text,
                'username': username,
                'image_url': msg.image.url if msg.image else None,
                'timestamp': timezone.now().strftime('%H:%M:%S %d/%m/%Y')
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'image': event['image_url'],
            'timestamp': event['timestamp'],
        }))

    @staticmethod
    async def get_user(username):
        from asgiref.sync import sync_to_async
        return await sync_to_async(CustomUser.objects.get)(username=username)

    @staticmethod
    async def get_chat(chat_id):
        from asgiref.sync import sync_to_async
        return await sync_to_async(ChatRoom.objects.get)(id=chat_id)
