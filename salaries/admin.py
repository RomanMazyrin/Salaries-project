from datetime import datetime

from django.contrib import admin
from django.contrib.admin import BooleanFieldListFilter
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.safestring import mark_safe

from salaries.models.EmployeePosition import EmployeePosition
from salaries.services.sheet_generators import (
    generate_tinkoff_payment_sheet_by_salary_reports,
)

from .models import Employee, EmployeeGroup, SalaryReport, Setting


class IsActiveFilter(BooleanFieldListFilter):
    def queryset(self, request, queryset):
        if self.used_parameters.get(self.lookup_kwarg) == 0:
            return queryset.filter(is_active=False)
        return queryset.filter(is_active=True)


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
    save_on_top = True


@admin.register(Setting)
class SettingAdminConfig(admin.ModelAdmin):
    list_display = ("name", "description")


@admin.action(description="Create Tinkoff payment sheet (.xslx)")
def create_payment_sheet(modeladmin, request, queryset):
    filename = "tinkoff_" + str(datetime.now().strftime("%d-%m-%Y %H:%M:%S")) + ".xlsx"
    result_file = generate_tinkoff_payment_sheet_by_salary_reports(queryset)
    response = HttpResponse(
        result_file,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = "attachment; filename=%s" % filename
    return response


@admin.action(description="Create copy")
def create_employee_position_copy(modeladmin, request, queryset):
    for model in queryset:
        model.pk = None
        model.position_name = model.position_name + " (Copy)"
        model.save()


class AdminSalaryReportStatusUpdateAction:
    def __init__(self, value, name):
        self.value = value
        self.__name__ = name

    def __call__(self, modeladmin, request, queryset):
        queryset.update(status=self.value)


def change_report_status_action_generator(status_list):
    for status in status_list:
        handler = admin.action(
            function=AdminSalaryReportStatusUpdateAction(
                status[0], f"AdminStatusUpdateAction.{status[0]}"
            ),
            description=f"Пометить отчет как {status[1]}",
        )
        yield handler


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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "employee":
            kwargs["queryset"] = Employee.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.display(empty_value=None, description="Способ выплаты")
    def payment_method(self, obj):
        paymenth_method_badge_link = obj.employee.get_payment_method_badge_link()
        return mark_safe('<img src="{}" />'.format(paymenth_method_badge_link))

    @admin.display(
        empty_value=None, description=Employee._meta.get_field("bank_account").verbose_name
    )
    def employee_bank_account(self, obj):
        bank_account = obj.employee.bank_account
        if bank_account is None:
            return ""
        return bank_account

    readonly_fields = ("slug_id", "employee_bank_account")
    list_display = (
        "instance_name",
        "employee",
        "status",
        "payment_method",
        "total_money",
        "employee_bank_account",
        "view_on_site_link",
        "created_at",
        "date_from",
        "date_to",
    )

    list_editable = ("status",)
    list_filter = ("employee",)

    actions = [
        create_payment_sheet,
        *change_report_status_action_generator(SalaryReport.REPORT_STATUSES),
    ]


class EmployeeInline(admin.StackedInline):
    model = Employee


admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = [EmployeeInline]


@admin.register(EmployeePosition)
class EmployeePositionAdmin(admin.ModelAdmin):
    list_display = ("position_name", "position_type")
    ordering = ("position_name",)
    actions = [create_employee_position_copy]


@admin.register(EmployeeGroup)
class EmployeeGroupAdmin(admin.ModelAdmin):
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in ("employee_list", "group_heads"):
            kwargs["queryset"] = Employee.objects.filter(is_active=True)
        return super().formfield_for_manytomany(db_field, request, **kwargs)
