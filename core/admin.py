from django.contrib import admin
from . import models
from django.contrib.auth.admin import UserAdmin
# Register your models here.


@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email']
