# Generated by Django 3.1.3 on 2020-11-19 20:03

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salaries', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='employee',
            options={'verbose_name': 'Сотрудник', 'verbose_name_plural': 'Сотрудники'},
        ),
        migrations.AddField(
            model_name='employee',
            name='one_call_cost',
            field=models.FloatField(blank=True, default=None, verbose_name='Стоимость одного звонка (рублей)'),
        ),
        migrations.AddField(
            model_name='employee',
            name='sale_fee_percent',
            field=models.FloatField(blank=True, default=None, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Процент с продаж'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='onpbx_id',
            field=models.IntegerField(blank=True, validators=[django.core.validators.MaxValueValidator(999), django.core.validators.MinValueValidator(100)]),
        ),
    ]
