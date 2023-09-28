import base64
import json
import secrets
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.core.files.base import ContentFile

from users.models import MyUser
from .models import Message, Chat, Room
from .serializers import MessageSerializer


class ChatConsumer(WebsocketConsumer):
    def __init__(self):
        self.room_uuid = None
        self.chat_group_name = None
        self.chat_uuid = None
        self.chat = None
        super().__init__()

    def connect(self):
        self.accept()
        self.room_uuid = self.scope["url_route"]["kwargs"]["uid"]
        close = False
        try:
            room = Room.objects.get(room_uuid=self.room_uuid)
            message = "Room is founded successfully!"
        except Room.DoesNotExist:
            message = "Room is not founded!"
            close = True
        self.send(text_data=json.dumps({
            'type': 'room_status',
            'message': message
        }))
        if close:
            self.close()

    def disconnect(self, close_code):
        # Leave room group
        if self.chat_group_name:
            async_to_sync(self.channel_layer.group_discard)(
                self.chat_group_name, self.channel_name
            )

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        # parse the json data into dictionary object
        text_data_json = json.loads(text_data)
        close = False
        if text_data_json["type"] == "chat_join":
            self.chat_uuid = text_data_json['uuid']
            try:
                self.chat = Chat.objects.get(chat_uuid=self.chat_uuid)
                message = "Join to the chat successfully!"
                self.chat_group_name = f"chat_{self.chat_uuid}"
                async_to_sync(self.channel_layer.group_add)(
                    self.chat_group_name, self.channel_name
                )
            except Chat.DoesNotExist:
                close = True
                message = "Chat is not founded!"
            self.send(text_data=json.dumps({
                'type': 'chat_join',
                'message': message
            }))
            if close:
                self.close()
        elif self.chat_group_name and text_data_json["type"] == "chat_message":
            # Send message to room group
            return_dict = {**text_data_json}
            async_to_sync(self.channel_layer.group_send)(
                self.chat_group_name,
                return_dict,
            )
        elif not self.chat_group_name:
            self.send(text_data=json.dumps({
                'type': 'chat_join',
                'message': "You are not join to any chat!",
            }))
        else:
            self.send(text_data=json.dumps({
                'type': 'chat_type',
                'message': "Chat type not supported!"
            }))

    # Receive message from room group
    def chat_message(self, event):
        text_data_json = event.copy()
        text_data_json.pop("type")
        message, attachment = (
            text_data_json["message"],
            text_data_json.get("attachment"),
        )

        # Attachment
        if attachment:
            file_str, file_ext = attachment["data"], attachment["format"]

            file_data = ContentFile(
                base64.b64decode(file_str), name=f"{secrets.token_hex(8)}.{file_ext}"
            )
            _message = Message.objects.create(
                attachment=file_data,
                text=message,
                chat=self.chat,
            )
        else:
            _message = Message.objects.create(
                text=message,
                chat=self.chat,
            )
        serializer = MessageSerializer(instance=_message)
        # Send message to WebSocket
        self.send(
            text_data=json.dumps(
                serializer.data
            )
        )
