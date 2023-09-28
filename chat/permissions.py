from rest_framework import permissions
from  .models import Membership


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

class IsMemberChatRoom(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            membership = Membership.objects.get(room=obj.room, member=request.user)
            return True
        except Membership.DoesNotExist:
            return False
