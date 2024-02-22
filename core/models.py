from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class AccountUserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, full_name, password, **extra_fields)


class Account(AbstractUser):
    full_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=255, unique=True)
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    objects = AccountUserManager()
