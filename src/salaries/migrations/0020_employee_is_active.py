# Generated by Django 3.2.11 on 2022-05-08 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salaries', '0019_auto_20220420_1827'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Активен'),
        ),
    ]
