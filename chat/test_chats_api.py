from django.contrib.auth import get_user_model
from django.test import TestCase
from users.utils import get_tokens_for_user
from rest_framework.test import APIClient
from chat.models import Room, Chat, Message, ChatOwnerToken, Chat, ChatOwner
from django.urls import reverse
from LeLuChat_ChatEngine.settings import DEFAULT_PREFIX_CHATOWNER_NAME
import json


class ChatApiTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email="test@example.com", password="pass")
        self.user_bearer_token = get_tokens_for_user(user=self.user)['access']
        self.room = Room.objects.create("test1", "http://test1.com", admin=self.user)
        self.chat = Chat.objects.create(self.room, "user1")
        self.messages = [(Message.objects.create(text="message_website_client", chat=self.chat, sender_object=self.chat.owner), 'website_client'),
                         (Message.objects.create(text="message_leluchat_user", chat=self.chat, sender_object=self.user), 'leluchat_user')]
        self.client = APIClient()

    def test_chat_list(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_bearer_token)
        resp = self.client.get(reverse('chat:chat_list', kwargs={'uid': str(self.room.room_uuid)}))
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['chat_owner']['name'], self.chat.owner.name)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.chat.owner.auth_token.key)
        resp = self.client.get(reverse('chat:chat_list', kwargs={'uid': str(self.room.room_uuid)}))
        self.assertEqual(resp.status_code, 401)

    def test_chat_create(self):
        resp = self.client.post(reverse('chat:chat_list', kwargs={'uid': str(self.room.room_uuid)}))
        data = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['chat_owner']['name'], DEFAULT_PREFIX_CHATOWNER_NAME + "2")

    def test_message_list(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.user_bearer_token)
        resp = self.client.get(reverse('chat:chat_detail', kwargs={'uid': str(self.chat.chat_uuid)}))
        data = resp.json()
        self.assertEqual(str(self.chat.chat_uuid), data['chat_uuid'])
        self.assertEqual(len(data['messages']), 2)
        for i, v in enumerate(data['messages']):
            self.assertEqual(self.messages[i][0].text, v['text'])
            self.assertEqual(None, v['attachment'])
            self.assertEqual(self.messages[i][1], v['sender']['type'])
            self.assertEqual(str(self.messages[i][0].sender_object), v['sender']['identity'])
