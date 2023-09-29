from channels.db import database_sync_to_async
from rest_framework_simplejwt.backends import TokenBackend
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import ValidationError
from .models import ChatOwnerToken
from users.models import MyUser

@database_sync_to_async
def get_user(token_name, token_key):
    if token_name == 'Token':
        try:
            token = ChatOwnerToken.objects.get(key=token_key)
            return token.user
        except ChatOwnerToken.DoesNotExist:
            return AnonymousUser()
    elif token_name == 'Bearer':
        try:
            valid_data = TokenBackend(algorithm='HS256').decode(token_key, verify=False)
            user_id = valid_data['user_id']
            try:
                return MyUser.objects.get(pk=user_id)
            except MyUser.DoesNotExist:
                return AnonymousUser()
        except ValidationError as v:
            return AnonymousUser()
    else:
        return AnonymousUser()

class TokensAuthMiddleware(BaseMiddleware):

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        if b'authorization' in headers:
            token_name, token_key = headers[b'authorization'].decode().split()
            scope['user'] = await get_user(token_name, token_key)
            scope['authorization_type'] = token_name
        else:
            scope['user'] = AnonymousUser()
            scope['authorization_type'] = None
        return await super().__call__(scope, receive, send)
