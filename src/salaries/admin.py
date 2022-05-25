from django.contrib import admin

from salaries.models.SipuniAccount import SipuniAccount
from .models import Employee
from .models import OnpbxAccount
from .models import Setting
from .models import SalaryReport
from django.contrib.admin import BooleanFieldListFilter
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class IsActiveFilter(BooleanFieldListFilter):
    def queryset(self, request, queryset):
        if self.used_parameters.get(self.lookup_kwarg) is None:
            return queryset.filter(is_active=True)
        return super().queryset(request, queryset)


@admin.register(Employee)
class EmployeeAdminConfig(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_editable = ('is_active',)
    list_filter = (
        ('is_active', IsActiveFilter),
    )


@admin.register(OnpbxAccount)
class OnpbxAccountAdminConfig(admin.ModelAdmin):
    pass


@admin.register(SipuniAccount)
class SipuniAccountAdminConfig(admin.ModelAdmin):
    pass


@admin.register(Setting)
class SettingAdminConfig(admin.ModelAdmin):
    list_display = ('name', 'description')


@admin.register(SalaryReport)
class SalaryReportAdminConfig(admin.ModelAdmin):

    @admin.display(description='Отчет')
    def instance_name(self, obj):
        formatted_date = obj.created_at.strftime('%d.%m.%Y (%H:%M)')
        return f"{obj.id}. {obj.employee.name}, {formatted_date}"

    @admin.display(empty_value=None, description='Итоговая сумма')
    def final_money(self, obj):
        metrica = obj.get_metrica_by('label', 'salary')
        if metrica:
            return f"{metrica.value:,}"
        return None

    readonly_fields = ('slug_id',)
    list_display = ('instance_name', 'date_from', 'date_to', 'status', 'final_money')
    list_editable = ('status',)

    def get_form(self, request, obj=None, **kwargs):
        form = super(SalaryReportAdminConfig, self).get_form(request, obj, **kwargs)
        form.base_fields['employee'].queryset = Employee.objects.filter(is_active=True)
        return form


class EmployeeInline(admin.StackedInline):
    model = Employee


admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = [EmployeeInline]