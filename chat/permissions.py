from rest_framework import permissions
from  .models import Membership, MyUser, ChatOwner
from rest_framework.exceptions import MethodNotAllowed


class IsGetAuthenticatedOrPost(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user and request.user.is_authenticated
        elif request.method == 'POST':
            return True
        else:
            raise MethodNotAllowed(request.method)
class IsReadOnlyMemberOrAdminMember(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        try:
            membership = Membership.objects.get(room=obj, member=request.user)
            if request.method in permissions.SAFE_METHODS:
                return True
            else:
                return membership.is_admin
        except Membership.DoesNotExist:
            return False

class IsMemberChatRoomOrChatowner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(request.user, MyUser):
            try:
                membership = Membership.objects.get(room=obj.room, member=request.user)
                return True
            except Membership.DoesNotExist:
                return False
        elif isinstance(request.user, ChatOwner):
            return obj.owner == request.user
        else:
            return False
