from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from .OnpbxAccount import OnpbxAccount


class Employee(models.Model):

    onpbx_id = models.IntegerField(blank=True, null=True, validators=[MaxValueValidator(999), MinValueValidator(100)])
    amocrm_id = models.IntegerField(blank=True, null=True)
    name = models.CharField('Имя', max_length=255)
    onpbx_account = models.ForeignKey(OnpbxAccount, on_delete=models.SET_NULL, null=True)
    daily_salary_amount = models.IntegerField("Дневной оклад", blank=True, null=True)
    one_hour_salary_amount = models.IntegerField("Стоимость часа работы", blank=True, null=True)
    one_call_cost = models.FloatField('Стоимость одного звонка (рублей)', blank=True, null=True, default=None)
    one_feedback_cost = models.IntegerField("Стоимость одного отзыва", blank=True, null=True)

    sale_fee_percent = models.FloatField(
        'Процент с продаж',
        blank=True,
        null=True,
        default=None,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
