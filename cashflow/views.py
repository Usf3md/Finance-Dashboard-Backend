from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import SAFE_METHODS
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404

from .permissions import IsMaker, IsMakerOrIsAdmin
from .serializers import MakerRunnerSerializer, OpeningSerializer, RunnerSerializer, TransactionDetailSerializer, TransactionSerializer, TransactionCUDSerializer
from .models import ROLES, TRANSACTION_STATUS, Opening, Runner, Transaction, TransactionDetail


class OpeningViewSet(ModelViewSet):
    queryset = Opening.objects.all()
    serializer_class = OpeningSerializer

    def get_permissions(self):
        permissions = [IsAuthenticated()]
        if self.request.method not in SAFE_METHODS:
            permissions += [IsMaker()]
        return permissions


class TransactionViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}

    def get_queryset(self):
        queryset = Transaction.objects.select_related(
            'transaction_detail').select_related('runner').all()

        runner = Runner.objects.get(user_id=self.request.user.id)
        if not IsMaker().has_permission(self.request, self):
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

    @action(detail=True, methods=['PATCH'], permission_classes=[IsMaker])
    def approve(self, request, pk):
        runner = Runner.objects.get(user_id=request.user.id)
        transaction = Transaction.objects.get(pk=pk)
        transaction.transaction_status = TRANSACTION_STATUS.APPROVED
        transaction.revisor = runner
        transaction.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['PATCH'], permission_classes=[IsMaker])
    def reject(self, request, pk):
        runner = Runner.objects.get(user_id=request.user.id)
        transaction = Transaction.objects.get(pk=pk)
        transaction.transaction_status = TRANSACTION_STATUS.REJECTED
        transaction.revisor = runner
        transaction.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TransactionDetailViewSet(ModelViewSet):
    queryset = TransactionDetail.objects.all()
    serializer_class = TransactionDetailSerializer

    def get_permissions(self):
        permissions = [IsAuthenticated()]
        if self.request.method not in SAFE_METHODS:
            permissions += [IsMaker()]
        return permissions


class RunnerViewSet(ModelViewSet):
    queryset = Runner.objects.select_related('user').all()
    permission_classes = [IsMakerOrIsAdmin]

    def get_serializer_class(self):
        if IsMakerOrIsAdmin().has_permission(self.request, self):
            return MakerRunnerSerializer
        return RunnerSerializer

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        runner = get_object_or_404(Runner, user_id=request.user.id)
        if request.method == 'GET':
            serializer = RunnerSerializer(runner)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = RunnerSerializer(runner, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
