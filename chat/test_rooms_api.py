from django.contrib.auth import get_user_model
from django.test import TestCase
from users.utils import get_tokens_for_user
from rest_framework.test import APIClient
from chat.models import Room
from django.urls import reverse
import json

def validate_room(response, room, member_email, member_index):
    return (response['uuid'] == str(room.room_uuid) and response['name'] == room.name and response['url'] == room.url
            and response['members'][member_index]['email'] == member_email and response['members'][member_index]['is_admin'])


class RoomApiTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email="test@example.com", password="pass")
        rs = [Room.objects.create("test1", "http://test1.com", admin=self.user),
                      Room.objects.create("test2", "http://test2.com", admin=self.user)]
        self.rooms = {}
        for r in rs:
            self.rooms[str(r.room_uuid)] = r
        self.client = APIClient()
        token = get_tokens_for_user(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token['access'])

    def test_room_list(self):
        resp = self.client.get("/engine/rooms/")
        data = resp.json()
        self.assertEqual(len(data), 2)
        for response in data:
            self.assertTrue(validate_room(response, self.rooms[response['uuid']], self.user.email, 0))

    def test_room_create(self):
        room_dict = {"name": "test3", "url": "https://test3.com"}
        resp = self.client.post(reverse('chat:room_list'), room_dict)
        r = Room.objects.get(room_uuid=resp.json()["uuid"])
        self.assertEqual(room_dict['name'], r.name)
        self.assertEqual(room_dict['url'], r.url)
        self.assertEqual(self.user, r.members.get(email=self.user.email))

    def test_room_detail(self):
        for k,v in self.rooms.items():
            resp = self.client.get(reverse('chat:room_detail', kwargs={'uid': k}))
            response = resp.json()
            self.assertTrue(validate_room(response, v, self.user.email, 0))

    def test_room_delete(self):
        r = Room.objects.create("test4", "https://test4.com", admin=self.user)
        resp = self.client.delete(reverse('chat:room_detail', kwargs={'uid': str(r.room_uuid)}))
        self.assertEqual(resp.status_code, 204)
        try:
            r = Room.objects.get(room_uuid=r.room_uuid)
            exist = True
        except Room.DoesNotExist:
            exist = False
        self.assertFalse(exist)

    def test_room_member_addition(self):
        r = Room.objects.create("test5", "http://test5.com", admin=self.user)
        user2 = get_user_model().objects.create_user(email="test2@example.com", password="pass2")
        members_dict = {'members': [{'email': user2.email, 'is_admin': "True"}]}
        resp = self.client.patch(reverse('chat:room_membership', kwargs={'uid': str(r.room_uuid)}),
                                 json.dumps(members_dict), content_type='application/json')
        response = resp.json()
        self.assertTrue(validate_room(response, r, user2.email, 1))

    def test_room_member_deletion(self):
        r = Room.objects.create("test6", "https://test6.com", admin=self.user)
        user2 = get_user_model().objects.create_user(email="test2@example.com", password="pass2")
        r.members.add(user2)
        members_dict = {'members': [{'email': user2.email}]}
        resp = self.client.post(reverse('chat:room_membership', kwargs={'uid': str(r.room_uuid)}),
                                 json.dumps(members_dict), content_type='application/json')
        room = resp.json()
        self.assertEqual(len(room['members']), 1)
