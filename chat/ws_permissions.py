from .models import Membership

def is_authorized(room, user, chat, authorization_type):
    if authorization_type == "Token":
        return chat.owner == user
    elif authorization_type == "Bearer":
        try:
            membership = Membership.objects.get(room=room, member=user)
            return True
        except Membership.DoesNotExist:
            return False
    else:
        return False
