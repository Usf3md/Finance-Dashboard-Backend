# Generated by Django 5.0.2 on 2024-03-09 02:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Opening',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('balance', models.DecimalField(decimal_places=2, max_digits=12)),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='RunnerRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='TransactionDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detail', models.CharField(max_length=512)),
            ],
            options={
                'ordering': ['detail'],
            },
        ),
        migrations.CreateModel(
            name='TransactionStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Runner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='cashflow.runnerrole')),
            ],
            options={
                'ordering': ['user__full_name'],
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField()),
                ('transaction_type', models.BooleanField(choices=[(True, 'Cash in'), (False, 'Cash out')])),
                ('note', models.TextField(null=True)),
                ('date', models.DateTimeField(auto_now=True)),
                ('image', models.CharField(max_length=512, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('opening', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cashflow.opening')),
                ('revisor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='revisions', to='cashflow.runner')),
                ('runner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='cashflow.runner')),
                ('transaction_detail', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='cashflow.transactiondetail')),
                ('transaction_status', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='cashflow.transactionstatus')),
            ],
            options={
                'ordering': ['pk'],
            },
        ),
    ]
