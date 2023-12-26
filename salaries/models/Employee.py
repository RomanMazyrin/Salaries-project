from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models

from .EmployeePosition import EmployeePosition


class Employee(models.Model):
    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    SELF_EMPLOYEED = "SELF_EMPLOYEED"
    CARD_PAYMENT = "CARD_PAYMENT"
    INDIVIDUAL_ENTERPRENEUR = "INDIVIDUAL_ENTERPRENEUR"

    PAYMENT_METHODS = {
        SELF_EMPLOYEED: ("Как самозанятому", "success"),
        INDIVIDUAL_ENTERPRENEUR: ("На счет ИП", "yellow"),
        CARD_PAYMENT: ("На карту", "important"),
    }

    PAYMENT_METHODS_FIELD_CHOICES = [(pm[0], pm[1][0]) for pm in PAYMENT_METHODS.items()]

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)

    amocrm_id = models.IntegerField(blank=True, null=True)

    position = models.ForeignKey(
        EmployeePosition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Позиция",
    )

    name = models.CharField("Имя", max_length=255)

    surname = models.CharField("Фамилия", max_length=255, default="")

    middlename = models.CharField("Отчество", max_length=255, default="")

    bank_account = models.CharField("Номер банковского счета", max_length=40, blank=True, null=True)

    bank_id = models.CharField(
        "БИК банка", max_length=12, blank=True, validators=[RegexValidator(regex=r"^\d{7,12}$")]
    )

    default_payment_details = models.TextField(
        "Назначение платежа по-умолчанию", blank=True, null=True
    )

    payment_method = models.CharField(
        "Способ выплаты",
        choices=PAYMENT_METHODS_FIELD_CHOICES,
        default=SELF_EMPLOYEED,
        max_length=50,
        blank=True,
        null=True,
    )

    is_active = models.BooleanField("Активен", blank=False, null=False, default=True)

    show_in_sales_plan = models.BooleanField(
        "Показывать в плане продаж", blank=False, null=False, default=True
    )

    def get_payment_method_badge_link(self):
        link_tmpl = "https://img.shields.io/badge/-{}-{}"
        payment_method_info = self.PAYMENT_METHODS.get(self.payment_method)
        if payment_method_info is None:
            return link_tmpl.format("Нет", "lightgrey")
        return link_tmpl.format(
            payment_method_info[0],
            payment_method_info[1],
        )

    def __str__(self):
        surname = self.surname if self.surname is not None else ""
        return f"{surname} {self.name}"
