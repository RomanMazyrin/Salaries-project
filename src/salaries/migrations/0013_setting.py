# Generated by Django 3.1.7 on 2021-12-23 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("salaries", "0012_employee_min_call_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Setting",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.SlugField(unique=True, verbose_name="Строковой идентификатор параметра"),
                ),
                ("value", models.TextField(verbose_name="Значение параметра")),
                (
                    "description",
                    models.CharField(max_length=1000, verbose_name="Описание параметра"),
                ),
            ],
            options={
                "verbose_name": "Настройка",
                "verbose_name_plural": "Настройки",
            },
        ),
    ]
