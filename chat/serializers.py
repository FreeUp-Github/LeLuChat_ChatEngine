from .models import Room, Membership, Chat, Message
from users.models import MyUser
from users.serializers import UserSerializer
from rest_framework import serializers


class RoomCreateSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(source='room_uuid', read_only=True)
    class Meta:
        model = Room
        fields = ["uuid", "url", "name"]

    def create(self, validated_data):
        return Room.objects.create(url=validated_data['url'], name=validated_data['name'], admin=validated_data['admin'])

class RoomSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    uuid = serializers.UUIDField(source='room_uuid', read_only=True)

    class Meta:
        model = Room
        fields = ["uuid", "url", "name", 'members']

    def get_members(self, obj):
        return UserMembershipSerializer(obj.members.all(), many=True, context={'room_id': obj.id}).data

    def update(self, instance, validated_data):
        return Room.objects.update_members(room=instance, members=validated_data['members'], add=validated_data['add'])

class UserMembershipSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = ['email', 'is_admin']

    def get_is_admin(self, obj):
        return obj.user_membership_room.get(room=self.context['room_id']).is_admin

class UpdateMembershipSerializer(serializers.Serializer):
    is_admin = serializers.BooleanField(default=False)
    email = serializers.EmailField(max_length=255)

class RoomUpdateMembershipSerializer(serializers.Serializer):
    members = UpdateMembershipSerializer(many=True)

    def update(self, instance, validated_data):
        return Room.objects.update_members(room=instance, members=validated_data['members'], add=validated_data['add'])

class RoomUpdateSerializer(serializers.ModelSerializer):
    members = UpdateMembershipSerializer(many=True)

    class Meta:
        model = Room
        fields = ['url', 'name', 'members']

    def update(self, instance, validated_data):
        return Room.objects.update(room=instance, name=validated_data['name'], url=validated_data['url'],
                                   members=validated_data['members'])

class ChatListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        exclude = ('room', 'id')

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        exclude = ('chat', 'id')

class ChatDetailSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True)
    class Meta:
        model = Chat
        exclude = ('room', 'id')
