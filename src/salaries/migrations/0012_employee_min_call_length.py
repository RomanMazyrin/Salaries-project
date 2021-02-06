# Generated by Django 3.1.7 on 2021-10-15 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("salaries", "0011_employee_one_feedback_cost"),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="min_call_length",
            field=models.IntegerField(
                blank=True,
                default=20,
                null=True,
                verbose_name="Минимальная длина звонка",
            ),
        ),
    ]
