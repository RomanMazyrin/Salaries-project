# Generated by Django 3.2.11 on 2023-02-01 09:04

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("salaries", "0035_auto_20221014_1816"),
    ]

    operations = [
        migrations.AddField(
            model_name="employeeposition",
            name="sales_plan_projects_count",
            field=models.IntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="План продаж (проекты) (количество)",
            ),
        ),
        migrations.AddField(
            model_name="employeeposition",
            name="sales_plan_projects_count_bonus",
            field=models.IntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="Бонус за выполнение плана продаж (проекты) (шт.)",
            ),
        ),
        migrations.AlterField(
            model_name="employeeposition",
            name="sales_plan_count",
            field=models.IntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="План продаж (лицензии + виджеты) (количество)",
            ),
        ),
        migrations.AlterField(
            model_name="employeeposition",
            name="sales_plan_count_bonus",
            field=models.IntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="Бонус за выполнение плана продаж (лицензии + виджеты) (шт.)",
            ),
        ),
    ]
