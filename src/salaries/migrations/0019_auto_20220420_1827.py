# Generated by Django 3.2.12 on 2022-04-20 15:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("salaries", "0018_auto_20220403_2255"),
    ]

    operations = [
        migrations.CreateModel(
            name="SipuniAccount",
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
                    "user_id",
                    models.CharField(max_length=255, verbose_name="ID пользователя (user_id)"),
                ),
                (
                    "secret_key",
                    models.CharField(max_length=255, verbose_name="Секретный ключ"),
                ),
            ],
            options={
                "verbose_name": "Аккаунт Sipuni",
                "verbose_name_plural": "Аккаунты Sipuni",
            },
        ),
        migrations.AddField(
            model_name="employee",
            name="sipuni_id",
            field=models.CharField(
                blank=True,
                default="",
                max_length=10,
                null=True,
                verbose_name="ID sipuni",
            ),
        ),
        migrations.AddField(
            model_name="employee",
            name="sipuni_account",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="salaries.sipuniaccount",
            ),
        ),
    ]
