from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission, IsAdminUser

from attendance.models import Member
from core.models import Account


class IsMember(BasePermission):
    def has_permission(self, request, view):
        member = get_object_or_404(Member, user_id=request.user.id)
        return bool(member)


class IsControl(BasePermission):
    def has_permission(self, request, view):
        account = get_object_or_404(Account, id=request.user.id)
        return account and account.is_control


class IsControlOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(IsControl().has_permission(request, view) or IsAdminUser().has_permission(request, view))


class IsMemberOrControlOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(IsMember().has_permission(request, view) or IsControlOrAdmin().has_permission(request, view))
