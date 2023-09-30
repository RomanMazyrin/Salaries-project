# Generated by Django 3.2.11 on 2022-09-09 11:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("salaries", "0032_auto_20220717_1629"),
    ]

    operations = [
        migrations.AddField(
            model_name="employeeposition",
            name="one_audit_commit_cost",
            field=models.IntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="Стоимость за назначение аудита",
            ),
        ),
    ]
