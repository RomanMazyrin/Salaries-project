# Generated by Django 3.2.11 on 2022-09-12 14:29

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("salaries", "0033_employeeposition_one_audit_commit_cost"),
    ]

    operations = [
        migrations.AddField(
            model_name="employeeposition",
            name="month_salary",
            field=models.IntegerField(
                blank=True,
                default=0,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="Месячный оклад",
            ),
        ),
    ]
