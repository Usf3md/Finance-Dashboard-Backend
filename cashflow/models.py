from django.db import models


class Runner(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['name']


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
        (True, "Cash in"),
        (False, "Cash out")
    ]
    opening = models.ForeignKey(Opening, on_delete=models.CASCADE)
    runner = models.ForeignKey(Runner, on_delete=models.SET_NULL, null=True)
    amount = models.PositiveIntegerField()
    transaction_type = models.BooleanField(choices=TRANSACTION_TYPES)
    transaction_detail = models.ForeignKey(
        TransactionDetail, on_delete=models.SET_NULL, null=True)
    note = models.TextField()
    date = models.DateTimeField(auto_now=True)
    image = models.CharField(max_length=512, null=True)

    def __str__(self) -> str:
        return f"Transaction #{str(self.id)}"

    class Meta:
        ordering = ['pk']
