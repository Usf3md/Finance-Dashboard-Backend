from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import OpeningSerializer, TransactionSerializer
from .models import Opening, Transaction


@api_view(['GET', 'POST'])
def opening_list(request):
    if request.method == 'GET':
        queryset = Opening.objects.all()
        serializer = OpeningSerializer(queryset, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = OpeningSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'DELETE'])
def opening(request, pk):
    opening = get_object_or_404(Opening, pk=pk)
    if request.method == 'GET':
        serializer = OpeningSerializer(opening)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        opening.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def transaction_list(request):
    if request.method == 'GET':
        queryset = Transaction.objects.select_related(
            'transaction_detail').all()
        serializer = TransactionSerializer(queryset, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = TransactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'DELETE'])
def transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'GET':
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        transaction.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
