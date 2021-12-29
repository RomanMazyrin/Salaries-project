from django.contrib import admin
from .models import Employee
from .models import OnpbxAccount
from .models import Setting


@admin.register(Employee)
class EmployeeAdminConfig(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(OnpbxAccount)
class OnpbxAccountAdminConfig(admin.ModelAdmin):
    pass


@admin.register(Setting)
class SettingAdminConfig(admin.ModelAdmin):
    list_display = ('name', 'description')