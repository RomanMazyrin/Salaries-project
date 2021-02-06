# Generated by Django 3.1.7 on 2021-04-01 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("salaries", "0009_employee_daily_salary_amount"),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="one_hour_salary_amount",
            field=models.IntegerField(blank=True, null=True, verbose_name="Стоимость часа работы"),
        ),
    ]
