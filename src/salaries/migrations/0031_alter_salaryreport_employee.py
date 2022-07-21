# Generated by Django 3.2.11 on 2022-07-17 00:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("salaries", "0030_alter_employee_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="salaryreport",
            name="employee",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="salaries.employee",
                verbose_name="Сотрудник",
            ),
        ),
    ]
