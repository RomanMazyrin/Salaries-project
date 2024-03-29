# Generated by Django 3.2.11 on 2022-07-16 13:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("salaries", "0028_auto_20220713_1758"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmployeeGroup",
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
                    "group_name",
                    models.CharField(max_length=250, verbose_name="Название группы"),
                ),
                (
                    "employee_list",
                    models.ManyToManyField(
                        related_name="groups_as_employee",
                        to="salaries.Employee",
                        verbose_name="Список участников",
                    ),
                ),
                (
                    "group_heads",
                    models.ManyToManyField(
                        related_name="groups_as_head",
                        to="salaries.Employee",
                        verbose_name="Список руководителей",
                    ),
                ),
            ],
            options={
                "verbose_name": "Группа сотрудников",
                "verbose_name_plural": "Группы сотрудников",
            },
        ),
    ]
