from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from .OnpbxAccount import OnpbxAccount


class Employee(models.Model):

    onpbx_id = models.IntegerField(blank=True, null=True, validators=[
                                   MaxValueValidator(999), MinValueValidator(100)])
    amocrm_id = models.IntegerField(blank=True, null=True)
    name = models.CharField('Имя', max_length=255)
    onpbx_account = models.ForeignKey(OnpbxAccount, on_delete=models.SET_NULL, null=True)
    daily_salary_amount = models.IntegerField("Дневной оклад", blank=True, null=True)
    one_hour_salary_amount = models.IntegerField("Стоимость часа работы", blank=True, null=True)
    one_call_cost = models.FloatField(
        'Стоимость одного звонка (рублей)', blank=True, null=True, default=None)
    one_feedback_cost = models.IntegerField("Стоимость одного отзыва", blank=True, null=True)
    min_call_length = models.IntegerField(
        "Минимальная длина звонка", blank=True, null=True, default=20)

    sale_fee_percent = models.FloatField(
        'Процент с продаж',
        blank=True,
        null=True,
        default=None,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    sales_plan = models.IntegerField("План продаж (в рублях)", blank=True, null=True)

    sale_fee_percent_above_plan = models.FloatField(
        'Процент с продаж сверх плана',
        blank=True,
        null=True,
        default=None,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    outcome_message_cost = models.IntegerField(
        "Стоимость исходящего сообщения",
        blank=True,
        null=True,
        default=0,
        validators=[MinValueValidator(0)]
    )

    cold_call_success_lead_cost = models.IntegerField(
        'Стоимость за успешную сделку по холодному обзвону',
        blank=True,
        null=True,
        default=0,
        validators=[MinValueValidator(0)]
    )

    audit_cost = models.IntegerField(
        'Стоимость аудита',
        blank=True,
        null=True,
        default=0,
        validators=[MinValueValidator(0)]
    )

    email_imap_address = models.CharField(
        "IMAP address", max_length=255, default='',
        blank=True, null=True
    )

    email_imap_login = models.CharField(
        'IMAP login', max_length=255, default='',
        blank=True, null=True
    )

    email_imap_password = models.CharField(
        'IMAP password', max_length=255, default='',
        blank=True, null=True
    )

    outcome_email_message_cost = models.IntegerField(
        "Стоимость исходящего email сообщения",
        blank=True,
        null=True,
        default=0,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
