# Generated by Django 3.2.11 on 2022-05-13 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salaries', '0020_employee_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='show_in_sales_plan',
            field=models.BooleanField(default=True, verbose_name='Показывать в плане продаж'),
        ),
    ]