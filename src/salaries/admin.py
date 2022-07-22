from django.contrib import admin
from django.http import HttpResponse
from salaries.models.EmployeePosition import EmployeePosition

from salaries.models.SipuniAccount import SipuniAccount
from .models import Employee, OnpbxAccount, Setting, SalaryReport, EmployeeGroup
from django.contrib.admin import BooleanFieldListFilter
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from salaries.services.sheet_generators import (
    generate_tinkoff_payment_sheet_by_salary_reports,
)
from datetime import datetime
from app.settings import MEDIA_ROOT
import os


class IsActiveFilter(BooleanFieldListFilter):
    def queryset(self, request, queryset):
        if self.used_parameters.get(self.lookup_kwarg) == 0:
            return Employee.objects.get_default_queryset().filter(is_active=False)
        return super().queryset(request, queryset)


class MembershipInline(admin.TabularInline):
    model = EmployeeGroup.employee_list.through
    verbose_name = "Группа"
    verbose_name_plural = "Группы"
    extra = 1


class MembershipAsHeadInline(admin.TabularInline):
    model = EmployeeGroup.group_heads.through
    verbose_name = "Руководитель группы"
    verbose_name_plural = "Руководитель групп"
    extra = 1


@admin.register(Employee)
class EmployeeAdminConfig(admin.ModelAdmin):
    list_display = ("name", "surname", "position", "is_active")
    list_editable = ("is_active",)
    list_filter = (("is_active", IsActiveFilter),)
    inlines = [MembershipInline, MembershipAsHeadInline]


@admin.register(OnpbxAccount)
class OnpbxAccountAdminConfig(admin.ModelAdmin):
    pass


@admin.register(SipuniAccount)
class SipuniAccountAdminConfig(admin.ModelAdmin):
    pass


@admin.register(Setting)
class SettingAdminConfig(admin.ModelAdmin):
    list_display = ("name", "description")


@admin.action(description="Create Tinkoff payment sheet (.xslx)")
def create_payment_sheet(modeladmin, request, queryset):
    filename = "tinkoff_" + str(datetime.now().strftime("%d-%m-%Y %H:%M:%S")) + ".xlsx"
    filepath = MEDIA_ROOT / filename
    generate_tinkoff_payment_sheet_by_salary_reports(filepath, queryset)
    response = HttpResponse(
        open(filepath, "rb"),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = "attachment; filename=%s" % filename
    os.remove(filepath)
    return response


@admin.register(SalaryReport)
class SalaryReportAdminConfig(admin.ModelAdmin):
    @admin.display(description="Отчет")
    def instance_name(self, obj):
        formatted_date = obj.created_at.strftime("%d.%m.%Y (%H:%M)")

        employee = obj.employee
        if not employee:
            employee = Employee()

        name = employee.name
        surname = employee.surname if employee.surname is not None else ""
        return f"{obj.id}. {surname} {name}, {formatted_date}"

    @admin.display(empty_value=None, description="Итоговая сумма")
    def total_money(self, obj):
        return obj.get_total_money()

    @admin.display(empty_value=None, description="Ссылка")
    def view_on_site_link(self, obj):
        url = obj.get_absolute_url()
        return mark_safe(f'<a href="{url}" target="_blank">Смотреть</a>')

    readonly_fields = ("slug_id",)
    list_display = (
        "instance_name",
        "employee",
        "created_at",
        "date_from",
        "date_to",
        "status",
        "total_money",
        "view_on_site_link",
    )
    list_editable = ("status",)
    list_filter = ("employee",)

    actions = [create_payment_sheet]


class EmployeeInline(admin.StackedInline):
    model = Employee


admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = [EmployeeInline]


@admin.register(EmployeePosition)
class EmployeePositionAdmin(admin.ModelAdmin):
    pass


@admin.register(EmployeeGroup)
class EmployeeGroupAdmin(admin.ModelAdmin):
    pass
