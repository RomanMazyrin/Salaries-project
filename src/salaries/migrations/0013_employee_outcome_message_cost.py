# Generated by Django 3.1.7 on 2021-12-17 17:33

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("salaries", "0012_employee_min_call_length"),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="outcome_message_cost",
            field=models.IntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="Стоимость исходящего сообщения",
            ),
        ),
    ]
