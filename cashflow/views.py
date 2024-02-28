from datetime import datetime, timezone
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import SAFE_METHODS
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404

from .permissions import IsChecker, IsCheckerOrIsAdmin, IsRunner
from .serializers import MODIFY_TIME_LIMIT, MakerRunnerSerializerReadWrite, MakerRunnerSerializerReadOnly, OpeningSerializer, RunnerRoleSerializer, RunnerSerializer, TransactionDetailSerializer, TransactionSerializer, TransactionCUDSerializer
from .models import TRANSACTION_STATUS, Opening, Runner, RunnerRole, Transaction, TransactionDetail, TransactionStatus


class OpeningViewSet(ModelViewSet):
    queryset = Opening.objects.all()
    serializer_class = OpeningSerializer

    def get_permissions(self):
        permissions = [IsAuthenticated(), IsRunner()]
        if self.request.method not in SAFE_METHODS:
            permissions += [IsChecker()]
        return permissions


class TransactionViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsRunner]

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}

    def get_queryset(self):
        queryset = Transaction.objects.select_related('transaction_detail').select_related(
            'transaction_status').select_related('runner').all()

        runner = Runner.objects.get(user_id=self.request.user.id)
        if not IsChecker().has_permission(self.request, self):
            queryset = queryset.filter(runner_id=runner.id)
        opening_id = self.request.query_params.get('openingId')
        try:
            if opening_id is not None:
                queryset = queryset.filter(opening_id=opening_id)
        except ValueError:
            return []
        return queryset

    def get_serializer_class(self):
        return TransactionSerializer if self.request.method in SAFE_METHODS else TransactionCUDSerializer

    @action(detail=True, methods=['PATCH'], permission_classes=[IsChecker])
    def approve(self, request, pk):
        runner = Runner.objects.get(user_id=request.user.id)
        transaction = Transaction.objects.get(pk=pk)
        transaction.transaction_status = get_object_or_404(
            TransactionStatus, status=TRANSACTION_STATUS.APPROVED)
        transaction.revisor = runner
        transaction.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['PATCH'], permission_classes=[IsChecker])
    def reject(self, request, pk):
        runner = Runner.objects.get(user_id=request.user.id)
        transaction = Transaction.objects.get(pk=pk)
        transaction.transaction_status = get_object_or_404(
            TransactionStatus, status=TRANSACTION_STATUS.REJECTED)
        transaction.revisor = runner
        transaction.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        transaction = self.get_queryset().get(pk=kwargs['pk'])
        current_time = datetime.now().astimezone(timezone.utc).replace(tzinfo=None)
        stored_time = transaction.created_at.astimezone(
            timezone.utc).replace(tzinfo=None)
        diff = current_time - stored_time
        if not IsChecker().has_permission(request, self):
            if diff > MODIFY_TIME_LIMIT:
                return Response(status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        transaction = self.get_queryset().get(pk=kwargs['pk'])
        current_time = datetime.now().astimezone(timezone.utc).replace(tzinfo=None)
        stored_time = transaction.created_at.astimezone(
            timezone.utc).replace(tzinfo=None)
        diff = current_time - stored_time
        if not IsChecker().has_permission(request, self):
            if diff > MODIFY_TIME_LIMIT:
                return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class TransactionDetailViewSet(ModelViewSet):
    queryset = TransactionDetail.objects.all()
    serializer_class = TransactionDetailSerializer

    def get_permissions(self):
        permissions = [IsAuthenticated(), IsRunner()]
        if self.request.method not in SAFE_METHODS:
            permissions += [IsChecker()]
        return permissions


class RunnerRoleViewSet(ModelViewSet):
    queryset = RunnerRole.objects.all()
    permission_classes = [IsCheckerOrIsAdmin]
    serializer_class = RunnerRoleSerializer


class RunnerViewSet(ModelViewSet):
    queryset = Runner.objects.select_related('user', 'role').all()
    permission_classes = [IsCheckerOrIsAdmin]

    def get_serializer_class(self):
        if IsCheckerOrIsAdmin().has_permission(self.request, self):
            return MakerRunnerSerializerReadOnly if self.request.method in SAFE_METHODS else MakerRunnerSerializerReadWrite

        return RunnerSerializer

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated, IsRunner])
    def me(self, request):
        runner = Runner.objects.get(user_id=request.user.id)
        if request.method == 'GET':
            serializer = RunnerSerializer(runner)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = RunnerSerializer(runner, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
