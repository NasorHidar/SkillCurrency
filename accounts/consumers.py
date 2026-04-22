import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ServiceAgreement, EncryptedMessage
from .utils import encrypt_message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.agreement_id = self.scope['url_route']['kwargs']['agreement_id']
        self.room_group_name = f'workspace_{self.agreement_id}'

        # Check authentication
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        # Check if user is part of the agreement
        is_authorized = await self.is_user_authorized(self.scope["user"], self.agreement_id)
        if not is_authorized:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = self.scope["user"].username

        # Encrypt and save to database
        await self.save_message(self.agreement_id, self.scope["user"], message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    @database_sync_to_async
    def is_user_authorized(self, user, agreement_id):
        try:
            agreement = ServiceAgreement.objects.get(id=agreement_id)
            return user == agreement.client or user == agreement.provider
        except ServiceAgreement.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, agreement_id, user, message):
        agreement = ServiceAgreement.objects.get(id=agreement_id)
        encrypted_text = encrypt_message(message)
        EncryptedMessage.objects.create(
            agreement=agreement,
            sender=user,
            encrypted_content=encrypted_text
        )
