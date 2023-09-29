from rest_framework.authentication import TokenAuthentication
from .models import ChatOwnerToken

class ChatownerTokenAuthentication(TokenAuthentication):
    model = ChatOwnerToken
