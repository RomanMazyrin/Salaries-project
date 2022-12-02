from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class EmployeePosition(models.Model):

    DEPRECATED = "DEPRECATED"
    SALES_MANAGER = "SALES_MANAGER"
    SALES_HEAD = "SALES_HEAD"
    FIXED_SALARY = "FIXED_SALARY"

    POSITION_TYPES = [
        (DEPRECATED, "Default (deprecated)"),
        (SALES_MANAGER, "Менеджер по продажам"),
        (SALES_HEAD, "РОП"),
        (FIXED_SALARY, "Сотрудник с фиксированным окладом"),
    ]

    position_name = models.CharField("Название позиции", max_length=255)

    position_type = models.CharField(
        "Тип позиции", choices=POSITION_TYPES, default=DEPRECATED, max_length=50
    )

    sales_plan_money = models.IntegerField(
        "План продаж (деньги)", blank=True, null=True, validators=[MinValueValidator(0)]
    )

    sales_plan_money_for_increased_percent = models.IntegerField(
        "План продаж для повышенного процента",
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )

    sales_plan_count = models.IntegerField(
        "План продаж (количество)",
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )

    presentation_meetings_plan_count = models.IntegerField(
        "План по встречам (количество)",
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )

    sales_plan_money_bonus = models.IntegerField(
        "Бонус за выполнение плана продаж ($)",
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )

    sales_plan_count_bonus = models.IntegerField(
        "Бонус за выполнение плана продаж (шт.)",
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )

    presentation_meetings_plan_count_bonus = models.IntegerField(
        "Бонус за выполнение плана по встречам (шт.)",
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )

    one_presentation_meeting_cost = models.IntegerField(
        "Стоимость проведения одной  встречи", blank=True, null=True
    )

    month_salary = models.IntegerField(
        "Месячный оклад", blank=True, null=False, default=0, validators=[MinValueValidator(0)]
    )

    one_hour_salary_amount = models.IntegerField("Стоимость часа работы", blank=True, null=True)

    one_feedback_cost = models.IntegerField("Стоимость одного отзыва", blank=True, null=True)

    sales_fee_percent = models.FloatField(
        "Процент с продаж",
        blank=True,
        null=True,
        default=None,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    sales_fee_percent_above_plan = models.FloatField(
        "Процент с продаж сверх плана",
        blank=True,
        null=True,
        default=None,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    cold_call_success_lead_cost = models.IntegerField(
        "Стоимость за успешную сделку по холодному обзвону",
        blank=True,
        null=True,
        default=0,
        validators=[MinValueValidator(0)],
    )

    license_activation_cost = models.IntegerField(
        "Стоимость за активацию лицензии",
        blank=True,
        null=True,
        default=0,
        validators=[MinValueValidator(0)],
    )

    one_audit_commit_cost = models.IntegerField(
        "Стоимость за назначение аудита",
        blank=True,
        null=True,
        default=0,
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        return self.position_name

    class Meta:
        verbose_name = "Позиция сотрудника"
        verbose_name_plural = "Позиции сотрудников"
