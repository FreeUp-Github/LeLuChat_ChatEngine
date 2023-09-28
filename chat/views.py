from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, get_list_or_404
from users.models import MyUser as User
from .models import Room, Chat
from .serializers import RoomCreateSerializer, RoomSerializer, RoomUpdateMembershipSerializer, RoomUpdateSerializer
from .serializers import ChatListSerializer, ChatDetailSerializer
from rest_framework import permissions
from django.db.models import Q
from django.shortcuts import redirect, reverse
from .permissions import IsReadOnlyMemberOrAdminMember, IsMemberChatRoom


class RoomList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        rooms = Room.objects.filter(members__email=request.user.email)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = RoomCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(admin=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoomDetail(APIView):
    permission_classes = [permissions.IsAuthenticated, IsReadOnlyMemberOrAdminMember]

    def get(self, request, id, format=None):
        room = get_object_or_404(Room, room_uuid=id)
        self.check_object_permissions(self.request, room)
        serializer = RoomSerializer(room)
        return Response(serializer.data)

    def put(self, request, uid, format=None):
        room = get_object_or_404(Room, room_uuid=uid)
        self.check_object_permissions(self.request, room)
        serializer = RoomUpdateSerializer(instance=room, data=request.data)
        if serializer.is_valid():
            serializer.save()
            serializer = RoomSerializer(room)
            return Response(serializer.data)

    def delete(self, request, uid, format=None):
        room = get_object_or_404(Room, room_uuid=uid)
        self.check_object_permissions(self.request, room)
        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RoomMembership(APIView):
    permission_classes = [permissions.IsAuthenticated, IsReadOnlyMemberOrAdminMember]

    def patch(self, request, uid, format=None):
        room = get_object_or_404(Room, room_uuid=uid)
        self.check_object_permissions(self.request, room)
        serializer = RoomUpdateMembershipSerializer(instance=room, data=request.data)
        if serializer.is_valid():
            serializer.save(add=True)
            serializer = RoomSerializer(room)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, uid, format=None):
        room = get_object_or_404(Room, room_uuid=uid)
        self.check_object_permissions(self.request, room)
        serializer = RoomUpdateMembershipSerializer(instance=room, data=request.data)
        if serializer.is_valid():
            serializer.save(add=False)
            serializer = RoomSerializer(room)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class ChatList(APIView):
    permission_classes = [permissions.IsAuthenticated, IsReadOnlyMemberOrAdminMember]

    def get(self, request, uid, format=None):
        room = get_object_or_404(Room, room_uuid=uid)
        self.check_object_permissions(self.request, room)
        serializer = ChatListSerializer(room.chats, many=True)
        return Response(serializer.data)

    def post(self, request, uid, format=None):
        room = get_object_or_404(Room, room_uuid=uid)
        chat = Chat(room=room)
        chat.save()
        serializer = ChatListSerializer(chat)
        return Response(serializer.data)

class ChatDetail(APIView):
    permission_classes = [permissions.IsAuthenticated, IsMemberChatRoom]
    def get(self, request, uid, format=None):
        chat = get_object_or_404(Chat, chat_uuid=uid)
        self.check_object_permissions(self.request, chat)
        serializer = ChatDetailSerializer(chat)
        return Response(serializer.data)
