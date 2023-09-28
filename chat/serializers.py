from .models import Room, Membership, Chat, Message, ChatOwner
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

class ChatOwnerSerializer(serializers.ModelSerializer):
    auth_token = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = ChatOwner
        fields = ('name', 'auth_token')
        read_only_fields = ('name', 'auth_token')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if self.context.get('not_token', True):
            ret.pop('auth_token')
        return ret

class ChatListSerializer(serializers.ModelSerializer):
    chat_owner = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Chat
        fields = ('chat_uuid', 'start_time', 'chat_owner')
        read_only_fields = ('chat_uuid', 'start_time')
    def create(self, validated_data):
        return Chat.objects.create(room=validated_data['room'], chatowner_name=validated_data['chatowner_name'])
    def get_chat_owner(self, obj):
        return ChatOwnerSerializer(obj.owner, context={'not_token': self.context.get('not_token', True)}).data

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        exclude = ('chat', 'id')

class ChatDetailSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    class Meta:
        model = Chat
        fields = ('chat_uuid', 'start_time', 'messages')
        read_only_fields = ('chat_uuid', 'start_time')
