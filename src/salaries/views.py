from django.forms import ModelForm
from django.http.response import HttpResponseForbidden
from django.views import generic, View
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from amocrm_components.ApiIterator import ApiIterator
from salaries.models.EmployeePosition import EmployeePosition
from salaries.models.SalaryReport import SalaryReport
from .models import Employee
from datetime import datetime
import pytz
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
import json
import math
from .services.DateIntervals.DashboardDateInterval import create_interval
from django.views.decorators.clickjacking import xframe_options_exempt
from salaries.services.SalaryCalculators.factories import (
    get_calculator_by_position_type,
)
from salaries.serializers import SalaryReportSerializer
from salaries.permissions import (
    ModelOwnerOrAdminOrHasPermPermission,
    HasEditPermission,
    CsrfExemptSessionAuthentication,
)
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.authentication import BasicAuthentication
from salaries.services.SalesPlanProgressCalculators import calculate_sales_plan_progress
from salaries.services.SalaryCalculators.constants import LEADS_FETCH_URL, AUTH_KEY


def get_all_active_employees():
    return Employee.objects.filter(is_active=True).order_by("pk")


class IndexView(LoginRequiredMixin, generic.ListView):
    def get_queryset(self):
        return get_all_active_employees().all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser or self.request.user.is_staff:
            if context["object_list"]:
                context["show_employees_calculate_form"] = True

        return context


class MyReportsListView(LoginRequiredMixin, generic.ListView):

    template_name = "salaries/salary_report_list.html"
    table_fields = ("__str__", "created_at", "status")
    context_object_name = "reports_list"

    def get_queryset(self):
        try:
            u_employee = self.request.user.employee
            return SalaryReport.objects.filter(employee=u_employee).order_by("-created_at").all()
        except Employee.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["table_fields"] = self.table_fields
        return context


class SalaryReportCreateView(LoginRequiredMixin, CreateView):
    model = SalaryReport

    fields = [
        field.name
        for field in SalaryReport._meta.get_fields()
        if field.name not in ["slug_id", "id"] and field.editable
    ]

    template_name = "salaries/salary_report_detail.html"


class SalaryReportView(LoginRequiredMixin, UserPassesTestMixin, DetailView):

    model = SalaryReport
    template_name = "salaries/salary_report_detail.html"
    slug_field = "slug_id"
    slug_url_kwarg = "report_slug"
    context_object_name = "report"

    def test_func(self):
        user = self.request.user
        report_query = {}
        report_query[self.slug_field] = self.kwargs[self.slug_url_kwarg]
        report = SalaryReport.objects.get(**report_query)
        result_condition = user.is_superuser or user.has_perm("salaries.view_salaryreport")
        if report:
            report_user = report.employee.user
            if report_user:
                result_condition = result_condition or report.employee.user.id == user.id
        return result_condition

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        context["report_link"] = "%s://%s%s" % (
            request.scheme,
            request.META["HTTP_HOST"],
            self.object.get_absolute_url(),
        )
        edit_permission = HasEditPermission()
        edit_permission = edit_permission.has_object_permission(request, self, self.object)
        context["can_edit"] = edit_permission

        return context


class SalaryReportForm(ModelForm):
    class Meta:
        model = SalaryReport
        fields = "__all__"
        exclude = ["slug_id"]


class SalaryResultView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        user = self.request.user
        result_condition = user.is_superuser or user.is_staff
        if not result_condition:
            employee = Employee.objects.get(pk=self.request.POST["employee_id"])
            result_condition = user.employee == employee

        return result_condition

    def post(self, request, *args, **kwargs):

        employee = get_object_or_404(Employee, pk=request.POST["employee_id"])

        timezone = pytz.timezone("Europe/Moscow")

        dt_from = timezone.localize(
            datetime.fromisoformat(request.POST["date_from"]).replace(hour=0, minute=0, second=0)
        )

        dt_to = timezone.localize(
            datetime.fromisoformat(request.POST["date_to"]).replace(hour=23, minute=59, second=59)
        )

        timestamp_from = dt_from.timestamp()
        timestamp_to = dt_to.timestamp()

        employee_position = employee.position
        if employee_position is None:
            employee_position_type = EmployeePosition.DEPRECATED
        else:
            employee_position_type = employee_position.position_type

        if employee_position_type == EmployeePosition.DEPRECATED:
            return render(
                request,
                "salaries/salary_result_error.html",
                {
                    "error_message": "{error}. Причина: {description}".format(
                        error="Не удалось сформировать отчет",
                        description="У сотрудника не корректная позиция",
                    )
                },
            )
        calculator = get_calculator_by_position_type(employee_position_type)
        report = calculator.process(employee, timestamp_from, timestamp_to)
        report.employee = employee
        report.date_from = dt_from
        report.date_to = dt_to

        return render(
            request,
            "salaries/salary_result.html",
            {"report": report, "save_form": SalaryReportForm(instance=report)},
        )


class SalesPlanView(View):
    @xframe_options_exempt
    def get(self, request, *args, **kwargs):

        auth_key = request.GET.get("auth_key")
        if auth_key != "eo485yngw8oer9jvwiertu6bei7ty":
            return HttpResponseForbidden("Access denied!")

        get_params = request.GET.dict()

        interval = create_interval(**get_params)

        excluded_amo_users = request.GET.getlist("excluded_users")

        f = ApiIterator(
            url=LEADS_FETCH_URL,
            params={
                "auth_key": AUTH_KEY,
                "filter": json.dumps(
                    {
                        "closed_at": {
                            "from": interval.get_timestamp_from(),
                            "to": interval.get_timestamp_to(),
                        },
                        "statuses": [
                            {"status_id": 142, "pipeline_id": 1212574},
                            {"status_id": 142, "pipeline_id": 1693621},
                            {"status_id": 142, "pipeline_id": 1693720},
                            {"status_id": 142, "pipeline_id": 3941655},
                            {"status_id": 142, "pipeline_id": 3346951},
                            {"status_id": 142, "pipeline_id": 3964107},
                            {"status_id": 142, "pipeline_id": 3678177},
                            {"status_id": 142, "pipeline_id": 4669350},
                        ],
                    }
                ),
            },
            entity_type="leads",
            fetch_limit=50,
        )

        leads = [lead for lead in f.get_next()]

        employees = (
            get_all_active_employees()
            .filter(show_in_sales_plan=True)
            .exclude(amocrm_id__in=excluded_amo_users)
            .all()
        )

        display_mods = {
            "percent": lambda actual, plan, percent: {
                "label": f"{percent}%",
                "bar_width": math.ceil(percent),
            },
            "money": lambda actual, plan, percent: {
                "label": f"{actual:,} руб.",
                "bar_width": 100,
            },
            "all": lambda actual, plan, percent: {
                "label": f"{actual:,} руб. / {plan:,} руб. ({percent}%)",
                "bar_width": math.ceil(percent),
            },
        }

        stats = []

        for employee in employees:
            stat = calculate_sales_plan_progress(employee, leads)

            display_stat_options = display_mods[request.GET.get("display_mode", "all")](
                stat["actual"], stat["plan"], stat["percent"]
            )
            if display_stat_options["bar_width"] < 20:
                display_stat_options["bar_width"] = 20

            stat.update(display_stat_options)
            stats.append(stat)

        return render(request, "amo_dashboards/sales_plan_progress.html", {"stats": stats})


@method_decorator(csrf_exempt, name="dispatch")
class SalaryReportApiView(generics.RetrieveUpdateAPIView):
    queryset = SalaryReport.objects.all()
    serializer_class = SalaryReportSerializer
    lookup_field = "slug_id"
    permission_classes = [ModelOwnerOrAdminOrHasPermPermission]
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
