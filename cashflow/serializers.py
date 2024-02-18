from rest_framework import serializers

from cashflow.models import Opening, Runner, Transaction, TransactionDetail


class RunnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Runner
        fields = ['id', 'name', 'email']


class OpeningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opening
        fields = ['id', 'date', 'balance']


class TransactionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionDetail
        fields = ['id', 'detail']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'opening', 'runner', 'amount', 'transaction_type',
                  'transaction_detail', 'note', 'date', 'image']
    transaction_detail = serializers.StringRelatedField()

    def validate(self, attrs):
        if attrs['amount'] < 0:
            raise serializers.ValidationError("Amount can't be negative.")
        return super().validate(attrs)
