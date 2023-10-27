from django.db import models
from django.conf import settings
from users.models import MyUser
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid

class RoomManager(models.Manager):
    def create(self, name, url, admin):
        room = Room(name=name, url=url)
        room.save()
        membership = Membership(room=room, member=admin, is_admin=True)
        membership.save()
        return room

    def update(self, room, name, url, members):
        room.name = name
        room.url = url
        room_members = room.members.all()
        email_isadmin = {}
        for member in members:
            email_isadmin[member['email']] = member['is_admin']
        for rm in room_members:
            if rm.email not in email_isadmin:
                user = get_object_or_404(MyUser, email=rm.email)
                room.members.remove(user)
            else:
                membership = Membership.objects.get(room=room, member=rm)
                if membership.is_admin != email_isadmin[rm.email]:
                    membership.is_admin = email_isadmin[rm.email]
                    membership.save()
                del email_isadmin[rm.email]
        for email, is_admin in email_isadmin.values():
            user = get_object_or_404(MyUser, email=email)
            membership = Membership(room=room, member=user, is_admin=is_admin)
            membership.save()
        return room

    def update_members(self, room, members, add):
        for member in members:
            user = get_object_or_404(MyUser, email=member['email'])
            if add:
                membership, created = Membership.objects.get_or_create(room=room, member=user)
                membership.is_admin = member['is_admin']
                membership.save()
            else:
                room.members.remove(user)
        return room


class Room(models.Model):
    name = models.CharField(max_length=50)
    members = models.ManyToManyField(MyUser, through="Membership", related_name="rooms")
    url = models.URLField(max_length=200, unique=True)
    room_uuid = models.UUIDField(unique=True, default=uuid.uuid4)

    objects = RoomManager()

    def __str__(self):
        return self.name


class Membership(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="room_membership")
    member = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="user_membership_room")
    is_admin = models.BooleanField(default=False)
    member_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['room', 'member'], name='unique membership')
        ]

class ChatOwnerManager(models.Manager):
    def create(self, name):
        chatowner = ChatOwner(name=name)
        chatowner.save()
        chatownertoken = ChatOwnerToken(user=chatowner)
        chatownertoken.save()
        return chatowner

class ChatOwner(models.Model):
    name = models.CharField(max_length=200, blank=False)
    is_active = models.BooleanField(default=True)

    @property
    def is_authenticated(self):
        return True

    objects = ChatOwnerManager()

    def __str__(self):
        return self.name

class ChatOwnerToken(Token):
    user = models.OneToOneField(ChatOwner, related_name='auth_token', on_delete=models.CASCADE,
                                verbose_name=_("User"))

    def __str__(self):
        return self.key

class ChatManager(models.Manager):
    def create(self, room, chatowner_name):
        chatowner = ChatOwner.objects.create(name=chatowner_name)
        chat = Chat(owner=chatowner, room=room)
        chat.save()
        return chat

class Chat(models.Model):
    owner = models.OneToOneField(ChatOwner, on_delete=models.SET_NULL, null=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, related_name='chats', null=True)
    chat_uuid = models.UUIDField(unique=True, default=uuid.uuid4)
    start_time = models.DateTimeField(auto_now_add=True)

    objects = ChatManager()

class Message(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    sender_object = GenericForeignKey("content_type", "object_id")
    text = models.CharField(max_length=200, blank=True)
    attachment = models.FileField(blank=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('timestamp',)
