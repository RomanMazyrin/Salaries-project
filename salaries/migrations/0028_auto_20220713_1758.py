# Generated by Django 3.2.11 on 2022-07-13 14:58

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("salaries", "0027_auto_20220702_0157"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmployeePosition",
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
                    "position_name",
                    models.CharField(max_length=255, verbose_name="Название позиции"),
                ),
                (
                    "position_type",
                    models.CharField(
                        choices=[
                            ("DEPRECATED", "Default (deprecated)"),
                            ("SALES_MANAGER", "Менеджер по продажам"),
                            ("SALES_HEAD", "РОП"),
                            ("TECH_SUPPORT", "Сотрудник технической поддержки"),
                        ],
                        default="DEPRECATED",
                        max_length=50,
                        verbose_name="Тип позиции",
                    ),
                ),
                (
                    "sales_plan_money",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="План продаж (деньги)",
                    ),
                ),
                (
                    "sales_plan_count",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="План продаж (количество)",
                    ),
                ),
                (
                    "presentation_meetings_plan_count",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="План по встречам (количество)",
                    ),
                ),
                (
                    "sales_plan_money_bonus",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Бонус за выполнение плана продаж ($)",
                    ),
                ),
                (
                    "sales_plan_count_bonus",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Бонус за выполнение плана продаж (шт.)",
                    ),
                ),
                (
                    "presentation_meetings_plan_count_bonus",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Бонус за выполнение плана по встречам (шт.)",
                    ),
                ),
                (
                    "one_presentation_meeting_cost",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Стоимость проведения одной  встречи",
                    ),
                ),
                (
                    "daily_salary_amount",
                    models.IntegerField(blank=True, null=True, verbose_name="Дневной оклад"),
                ),
                (
                    "one_hour_salary_amount",
                    models.IntegerField(
                        blank=True, null=True, verbose_name="Стоимость часа работы"
                    ),
                ),
                (
                    "one_feedback_cost",
                    models.IntegerField(
                        blank=True, null=True, verbose_name="Стоимость одного отзыва"
                    ),
                ),
                (
                    "sales_fee_percent",
                    models.FloatField(
                        blank=True,
                        default=None,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100),
                        ],
                        verbose_name="Процент с продаж",
                    ),
                ),
                (
                    "sales_fee_percent_above_plan",
                    models.FloatField(
                        blank=True,
                        default=None,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100),
                        ],
                        verbose_name="Процент с продаж сверх плана",
                    ),
                ),
                (
                    "cold_call_success_lead_cost",
                    models.IntegerField(
                        blank=True,
                        default=0,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Стоимость за успешную сделку по холодному обзвону",
                    ),
                ),
                (
                    "license_activation_cost",
                    models.IntegerField(
                        blank=True,
                        default=0,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Стоимость за активацию лицензии",
                    ),
                ),
            ],
            options={
                "verbose_name": "Позиция сотрудника",
                "verbose_name_plural": "Позиции сотрудников",
            },
        ),
        migrations.AddField(
            model_name="employee",
            name="position",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="salaries.employeeposition",
                verbose_name="Позиция",
            ),
        ),
    ]
