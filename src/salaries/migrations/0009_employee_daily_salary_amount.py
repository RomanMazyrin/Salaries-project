# Generated by Django 3.1.7 on 2021-04-01 12:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("salaries", "0008_auto_20201120_0120"),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="daily_salary_amount",
            field=models.IntegerField(blank=True, null=True, verbose_name="Дневной оклад"),
        ),
    ]
