# Generated by Django 3.1.3 on 2020-11-19 20:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salaries', '0006_auto_20201119_2306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='sale_fee_percent',
            field=models.FloatField(blank=True, default=None, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Процент с продаж'),
        ),
    ]