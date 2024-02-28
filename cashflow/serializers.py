from datetime import datetime, timedelta, timezone
from rest_framework import serializers
from cashflow.models import ROLES, TRANSACTION_STATUS, Opening, Runner, RunnerRole, Transaction, TransactionDetail, TransactionStatus


MODIFY_TIME_LIMIT = timedelta(minutes=5)


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

    role = serializers.StringRelatedField(read_only=True)


class MakerRunnerSerializerReadOnly(RunnerSerializer):
    user = None


class MakerRunnerSerializerReadWrite(MakerRunnerSerializerReadOnly):
    user = None
    role = None


class RunnerRoleSerializer(serializers.Serializer):
    class Meta:
        model = RunnerRole
        fields = ['id', 'label']


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
                  'transaction_detail', 'transaction_status', 'revisor', 'note', 'date', 'image', 'remaining_time']
    runner = RunnerSerializer(read_only=True)
    transaction_detail = serializers.StringRelatedField()
    transaction_status = serializers.StringRelatedField()
    revisor = RunnerSerializer(read_only=True)
    remaining_time = serializers.SerializerMethodField(
        method_name='calculate_remaining_time')

    def calculate_remaining_time(self, transaction: Transaction):
        current_time = datetime.now().astimezone(timezone.utc).replace(tzinfo=None)
        stored_time = transaction.created_at.astimezone(
            timezone.utc).replace(tzinfo=None)
        diff = current_time - stored_time
        if diff > MODIFY_TIME_LIMIT:
            return 0
        return int((MODIFY_TIME_LIMIT - diff).seconds)

    def to_internal_value(self, data):
        try:
            for key in data:
                if data[key] == '':
                    data[key] = None
        except:
            pass
        return super().to_internal_value(data)

    def validate(self, attrs):
        if attrs['amount'] < 0:
            raise serializers.ValidationError("Amount can't be negative.")
        return super().validate(attrs)

    def create(self, validated_data):
        runner = Runner.objects.select_related(
            'role').get(user_id=self.context['user_id'])
        runner_role = runner.role.role
        status = TRANSACTION_STATUS.APPROVED if runner_role == ROLES.CHECKER else TRANSACTION_STATUS.PENDING
        transaction_status = TransactionStatus.objects.get(status=status)
        revisor = runner if runner_role == ROLES.CHECKER else None
        transaction = Transaction(
            runner_id=runner.id, transaction_status=transaction_status, revisor=revisor, **validated_data)
        transaction.save()
        return transaction


class TransactionCUDSerializer(TransactionSerializer):
    transaction_detail = serializers.PrimaryKeyRelatedField(
        queryset=TransactionDetail.objects.all()
    )
