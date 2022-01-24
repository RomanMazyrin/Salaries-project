# Generated by Django 3.1.3 on 2020-11-19 20:04

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salaries', '0002_auto_20201119_2303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='amocrm_id',
            field=models.IntegerField(blank=True, default=None),
        ),
        migrations.AlterField(
            model_name='employee',
            name='onpbx_id',
            field=models.IntegerField(blank=True, default=None, validators=[django.core.validators.MaxValueValidator(999), django.core.validators.MinValueValidator(100)]),
        ),
    ]