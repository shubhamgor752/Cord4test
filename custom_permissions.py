from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from group.models import CustomGroup

class GroupAccess(BasePermission):
    message = "You do not have permission to perform this action"

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user == "pass":
            pass