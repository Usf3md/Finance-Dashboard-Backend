from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission, IsAdminUser, IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist

from .models import ROLES, Runner, RunnerRole


class IsRunner(BasePermission):
    def has_permission(self, request, view):
        runner = get_object_or_404(Runner, user_id=request.user.id)
        return bool(runner)


class IsChecker(BasePermission):
    def has_permission(self, request, view):
        runner = get_object_or_404(Runner, user_id=request.user.id)
        runner_role = RunnerRole.objects.get(id=runner.role.id).role
        return bool(runner and runner_role == ROLES.CHECKER)


class IsCheckerOrIsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(IsChecker().has_permission(request, view) or IsAdminUser().has_permission(request, view))
