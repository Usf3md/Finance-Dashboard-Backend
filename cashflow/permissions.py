from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission, IsAdminUser

from .models import ROLES, Runner


class IsMaker(BasePermission):
    def has_permission(self, request, view):
        runner = get_object_or_404(Runner, user_id=request.user.id)
        return bool(runner and runner.role == ROLES.MAKER)


class IsMakerOrIsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(IsMaker().has_permission(request, view) or IsAdminUser().has_permission(request, view))
