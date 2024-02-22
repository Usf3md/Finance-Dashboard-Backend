from rest_framework import serializers
from cashflow.models import ROLES, TRANSACTION_STATUS, Opening, Runner, Transaction, TransactionDetail
from cashflow.permissions import IsMaker


class RunnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Runner
        fields = ['id', 'user', 'full_name', 'email', 'role', 'is_admin']
    full_name = serializers.SlugRelatedField(read_only=True,
                                             slug_field='full_name', source='user')
    email = serializers.SlugRelatedField(read_only=True,
                                         slug_field='email', source='user')
    is_admin = serializers.SlugRelatedField(read_only=True,
                                            slug_field='is_staff', source='user')

    user = serializers.PrimaryKeyRelatedField(read_only=True)

    role = serializers.CharField(read_only=True)


class MakerRunnerSerializer(RunnerSerializer):
    role = None
    user = None


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
                  'transaction_detail', 'transaction_status', 'revisor', 'note', 'date', 'image']
    runner = RunnerSerializer(read_only=True)
    transaction_detail = serializers.StringRelatedField(read_only=True)
    transaction_status = serializers.CharField(read_only=True)
    revisor = RunnerSerializer(read_only=True)

    def validate(self, attrs):
        if attrs['amount'] < 0:
            raise serializers.ValidationError("Amount can't be negative.")
        return super().validate(attrs)


class TransactionCUDSerializer(TransactionSerializer):
    transaction_detail = serializers.PrimaryKeyRelatedField(
        queryset=TransactionDetail.objects.all()
    )

    def create(self, validated_data):
        runner = Runner.objects.get(user_id=self.context['user_id'])
        transaction_status = TRANSACTION_STATUS.PENDING if runner.role == ROLES.CHECKER else TRANSACTION_STATUS.APPROVED
        transaction = Transaction(
            runner_id=runner.id, transaction_status=transaction_status, **validated_data)
        transaction.save()
        return transaction
