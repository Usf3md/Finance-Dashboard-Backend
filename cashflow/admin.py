from django.contrib import admin
from . import models
# Register your models here.


@admin.register(models.Runner)
class RunnerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email']


@admin.register(models.Opening)
class OpeningAdmin(admin.ModelAdmin):
    list_display = ['date', 'balance']


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['runner', 'amount', 'opening', 'transaction_type']


@admin.register(models.TransactionDetail)
class TransactionDetailAdmin(admin.ModelAdmin):
    pass
