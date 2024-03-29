# Generated by Django 3.1.3 on 2020-11-19 20:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("salaries", "0005_auto_20201119_2306"),
    ]

    operations = [
        migrations.AlterField(
            model_name="employee",
            name="one_call_cost",
            field=models.FloatField(
                blank=True,
                default=None,
                null=True,
                verbose_name="Стоимость одного звонка (рублей)",
            ),
        ),
    ]
