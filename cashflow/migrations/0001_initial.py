# Generated by Django 5.0 on 2024-02-26 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
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
            name='Runner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('m', 'Maker'), ('c', 'Checker')], max_length=1)),
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
                ('transaction_status', models.CharField(choices=[('r', 'Rejected'), ('a', 'Approved'), ('p', 'Pending')], max_length=1)),
            ],
            options={
                'ordering': ['pk'],
            },
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
    ]
