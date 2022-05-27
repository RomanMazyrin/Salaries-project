# Generated by Django 3.2.11 on 2022-05-27 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salaries', '0024_alter_employee_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salaryreport',
            name='status',
            field=models.CharField(choices=[('NOT_CONFIRMED', 'Не подтвержден'), ('CONFIRMED_FOR_PAYMENT', 'Подтвержден для оплаты'), ('PAID', 'Оплачен'), ('DECLINED', 'Отклонен')], default='NOT_CONFIRMED', max_length=50, verbose_name='Статус'),
        ),
    ]
