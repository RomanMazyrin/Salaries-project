from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import BasePermission


class HasEditPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        result_condition = user.is_superuser or user.has_perm("salaries.change_salaryreport")
        return result_condition


class ModelOwnerOrAdminOrHasPermPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        result_condition = user.is_superuser or user.has_perm("salaries.view_salaryreport")
        report_user = obj.employee.user
        if report_user:
            result_condition = result_condition or obj.employee.user.id == user.id
        return result_condition


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return
