from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import User

from salaries.models.SipuniAccount import SipuniAccount
from .OnpbxAccount import OnpbxAccount


class Employee(models.Model):

    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, null=True, blank=True)

    onpbx_id = models.IntegerField(blank=True, null=True, validators=[
                                   MaxValueValidator(999), MinValueValidator(100)])

    sipuni_id = models.CharField('ID sipuni', blank=True, null=True, default='', max_length=10)

    amocrm_id = models.IntegerField(blank=True, null=True)

    name = models.CharField('Имя', max_length=255)
    surname = models.CharField('Фамилия', max_length=255, blank=True, null=True)
    middlename = models.CharField('Отчество', max_length=255, blank=True, null=True)

    bank_account = models.CharField('Номер банковского счета', max_length=40, blank=True, null=True)
    default_payment_details = models.TextField(
        'Назначение платежа по-умолчанию',
        blank=True,
        null=True
    )

    onpbx_account = models.ForeignKey(OnpbxAccount, on_delete=models.SET_NULL, null=True, blank=True)
    sipuni_account = models.ForeignKey(SipuniAccount, on_delete=models.SET_NULL, null=True, blank=True)

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

    license_activation_cost = models.IntegerField(
        'Стоимость за активацию лицензии',
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

    is_active = models.BooleanField(
        'Активен',
        blank=False,
        null=False,
        default=True
    )

    show_in_sales_plan = models.BooleanField(
        'Показывать в плане продаж',
        blank=False,
        null=False,
        default=True
    )

    def __str__(self):
        surname = self.surname if self.surname is not None else ''
        return f"{surname} {self.name}"

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
