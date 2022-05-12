from django.contrib import admin

from salaries.models.SipuniAccount import SipuniAccount
from .models import Employee
from .models import OnpbxAccount
from .models import Setting
from django.contrib.admin import BooleanFieldListFilter

class IsActiveFilter(BooleanFieldListFilter):
    def queryset(self, request, queryset):
        if self.used_parameters.get(self.lookup_kwarg) == None:
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
