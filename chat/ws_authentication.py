from channels.db import database_sync_to_async
from rest_framework_simplejwt.backends import TokenBackend
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import ValidationError
from .models import ChatOwnerToken
from users.models import MyUser


def _get_user(token_name, token_key):
    if token_name == 'Token':
        try:
            token = ChatOwnerToken.objects.get(key=token_key)
            return token.user, token_name
        except ChatOwnerToken.DoesNotExist:
            return AnonymousUser(), None
    elif token_name == 'Bearer':
        try:
            valid_data = TokenBackend(algorithm='HS256').decode(token_key, verify=False)
            user_id = valid_data['user_id']
            try:
                return MyUser.objects.get(pk=user_id), token_name
            except MyUser.DoesNotExist:
                return AnonymousUser(), None
        except ValidationError as v:
            return AnonymousUser(), None
    else:
        return AnonymousUser(), None


class TokenAuthentication:

    @classmethod
    def authenticate(cls, token):
        try:
            token_name, token_key = token.split()
            user, authorization_type = _get_user(token_name, token_key)
            return user, authorization_type
        except Exception:
            return AnonymousUser(), None
