# Generated by Django 3.2.11 on 2023-05-01 16:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("salaries", "0036_auto_20230201_1204"),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="payment_method",
            field=models.CharField(
                blank=True,
                choices=[
                    ("BANK_ACCOUNT_PAYMENT", "На расчетный счет"),
                    ("CARD_PAYMENT", "На карту"),
                ],
                default="BANK_ACCOUNT_PAYMENT",
                max_length=50,
                null=True,
                verbose_name="Способ выплаты",
            ),
        ),
    ]
