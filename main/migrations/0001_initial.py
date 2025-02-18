# Generated by Django 5.1.6 on 2025-02-18 08:06

import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('sponsor_type', models.CharField(choices=[('individual', 'Individual'), ('legal_entity', 'Legal Entity')], max_length=50)),
                ('full_name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=13)),
                ('payment_type', models.CharField(choices=[('cash', 'Cash'), ('debit_card', 'Debit Card'), ('bank_transfer', 'Bank Transfer')], max_length=20)),
                ('total_sponsorship_amount', models.FloatField(validators=[django.core.validators.MinValueValidator(500000)])),
                ('status', models.CharField(choices=[('new', 'New'), ('in_progress', 'In Progress'), ('verified', 'Verified'), ('cancelled', 'Cancelled')], default='new', max_length=50)),
                ('company_name', models.CharField(blank=True, max_length=150, null=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Sponsor',
                'verbose_name_plural': 'Sponsors',
                'db_table': 'sponsors',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('full_name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=13)),
                ('university', models.CharField(max_length=100)),
                ('degree', models.CharField(choices=[('bachelor', "Bachelor's degree"), ('master', "Master's degree")], max_length=10)),
                ('tuition_fee', models.FloatField()),
            ],
            options={
                'verbose_name': 'Student',
                'verbose_name_plural': 'Students',
                'db_table': 'students',
            },
        ),
        migrations.CreateModel(
            name='StudentSponsor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allocated_money', models.FloatField()),
                ('sponsor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.sponsor')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.student')),
            ],
            options={
                'verbose_name': 'Student sponsor',
                'verbose_name_plural': 'Student sponsors',
                'db_table': 'student_sponsors',
            },
        ),
    ]
