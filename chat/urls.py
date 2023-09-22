from django.urls import path
from . import views

app_name = 'chat'
urlpatterns = [
    path('rooms/', views.RoomList.as_view(), name='room_list'),
    path('rooms/<uuid:uid>/', views.RoomDetail.as_view(), name='room_detail'),
    path('rooms/<uuid:uid>/members', views.RoomMembership.as_view(), name='room_membership'),
    path('rooms/<uuid:uid>/chats/', views.ChatList.as_view(), name='chat_list')
]
