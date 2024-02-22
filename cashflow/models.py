from django.db import models
from django.conf import settings
from django.contrib import admin


class ROLES:
    MAKER = 'm'
    CHECKER = 'c'


class TRANSACTION_STATUS:
    PENDING = 'p'
    APPROVED = 'a'
    REJECTED = 'r'


class Runner(models.Model):
    ROLES_CHOICES = [
        (ROLES.MAKER, 'Maker'),
        (ROLES.CHECKER, 'Checker'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    role = models.CharField(max_length=1, choices=ROLES_CHOICES)

    @admin.display(ordering='user__full_name')
    def full_name(self):
        return self.user.full_name

    @admin.display(ordering='user__email')
    def email(self):
        return self.user.email

    def __str__(self) -> str:
        return self.user.full_name

    class Meta:
        ordering = ['user__full_name']


class Opening(models.Model):
    date = models.DateTimeField()
    balance = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self) -> str:
        return str(self.date)

    class Meta:
        ordering = ['date']


class TransactionDetail(models.Model):
    detail = models.CharField(max_length=512)

    def __str__(self) -> str:
        return self.detail

    class Meta:
        ordering = ['detail']


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        (True, 'Cash in'),
        (False, 'Cash out')
    ]
    TRANSACTION_STATUS_CHOICES = [
        (TRANSACTION_STATUS.REJECTED, 'Rejected'),
        (TRANSACTION_STATUS.APPROVED, 'Approved'),
        (TRANSACTION_STATUS.PENDING, 'Pending'),
    ]
    opening = models.ForeignKey(Opening, on_delete=models.CASCADE)
    runner = models.ForeignKey(Runner, on_delete=models.SET_NULL, null=True)
    amount = models.PositiveIntegerField()
    transaction_type = models.BooleanField(choices=TRANSACTION_TYPES)
    transaction_detail = models.ForeignKey(
        TransactionDetail, on_delete=models.SET_NULL, null=True)
    note = models.TextField(null=True)
    date = models.DateTimeField(auto_now=True)
    image = models.CharField(max_length=512, null=True)
    transaction_status = models.CharField(
        max_length=1, choices=TRANSACTION_STATUS_CHOICES)
    revisor = models.ForeignKey(
        Runner, on_delete=models.SET_NULL, null=True, related_name='revisions')

    def __str__(self) -> str:
        return f'Transaction #{str(self.id)}'

    class Meta:
        ordering = ['pk']
