# Generated by Django 3.2.11 on 2022-05-21 21:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("salaries", "0022_salaryreport"),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="user",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="salaryreport",
            name="metrics",
            field=models.JSONField(blank=True, default="", verbose_name="Метрики"),
        ),
    ]