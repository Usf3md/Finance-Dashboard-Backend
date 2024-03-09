from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission, IsAdminUser

from attendance.models import Member
from core.models import Account


class IsMember(BasePermission):
    def has_permission(self, request, view):
        try:
            member = Member.objects.get(user_id=request.user.id)
            return bool(member)
        except Member.DoesNotExist:
            return False


class IsControl(BasePermission):
    def has_permission(self, request, view):
        try:
            account = Account.objects.get(id=request.user.id)
            return account.is_control
        except Account.DoesNotExist:
            return False


class IsControlOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(IsControl().has_permission(request, view) or IsAdminUser().has_permission(request, view))


class IsMemberOrControlOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(IsMember().has_permission(request, view) or IsControlOrAdmin().has_permission(request, view))
