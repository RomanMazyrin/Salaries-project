import asyncio
from django.forms import ModelForm
from django.http.response import HttpResponse
from django.views import generic, View
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.shortcuts import render, get_object_or_404

from amocrm_components.ApiIterator import ApiIterator
from salaries.models.SalaryReport import SalaryReport
from .models import Employee
from datetime import datetime
from packages.Onlinepbx.Client import Client as OnpbxClient
from salaries.services.SalaryCounter import SalaryCounter
import pytz
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
import json
import math
from .services.DateIntervals.DashboardDateInterval import create_interval
from django.views.decorators.clickjacking import xframe_options_exempt


def get_all_active_employees():
    return Employee.objects.filter(is_active=True).order_by("pk")


class IndexView(LoginRequiredMixin, generic.ListView):
    def get_queryset(self):
        return get_all_active_employees().all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context)
        if self.request.user.is_superuser or self.request.user.is_staff:
            if context['object_list']:
                context['show_employees_calculate_form'] = True

        return context


class MyReportsListView(LoginRequiredMixin, generic.ListView):

    template_name = 'salaries/salary_report_list.html'
    table_fields = ('__str__', 'created_at', 'status')
    context_object_name = 'reports_list'

    def get_queryset(self):
        return (
            SalaryReport.objects
            .filter(employee=self.request.user.employee)
            .order_by('created_at')
            .all()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table_fields'] = self.table_fields
        return context


class SalaryReportCreateView(LoginRequiredMixin, CreateView):
    model = SalaryReport

    fields = [
        field.name for field in SalaryReport._meta.get_fields()
        if field.name not in ['slug_id', 'id'] and field.editable
    ]

    template_name = 'salaries/salary_report_detail.html'


class SalaryReportView(LoginRequiredMixin, UserPassesTestMixin, DetailView):

    model = SalaryReport
    template_name = 'salaries/salary_report_detail.html'
    slug_field = 'slug_id'
    slug_url_kwarg = 'report_slug'
    context_object_name = 'report'

    def test_func(self):
        user = self.request.user
        report_query = {}
        report_query[self.slug_field] = self.kwargs[self.slug_url_kwarg]
        report = SalaryReport.objects.get(**report_query)
        result_condition = user.is_superuser or user.has_perm('salaries.view_salaryreport')
        if report:
            report_user = report.employee.user
            if report_user:
                result_condition = result_condition or report.employee.user.id == user.id
        return result_condition

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        context['report_link'] = "%s://%s%s" % (
            request.scheme,
            request.META['HTTP_HOST'],
            self.object.get_absolute_url()
        )
        return context


class SalaryReportForm(ModelForm):
    class Meta:
        model = SalaryReport
        fields = '__all__'
        exclude = ['slug_id']


class SalaryResultView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        user = self.request.user
        result_condition = user.is_superuser or user.is_staff
        if not result_condition:
            employee = Employee.objects.get(pk=self.request.POST['employee_id'])
            result_condition = user.employee == employee

        return result_condition

    def post(self, request, *args, **kwargs):

        employee = get_object_or_404(Employee, pk=request.POST['employee_id'])

        timezone = pytz.timezone("Europe/Moscow")

        dt_from = timezone.localize(
            datetime
            .fromisoformat(request.POST['date_from'])
            .replace(hour=0, minute=0, second=0)
        )

        dt_to = timezone.localize(
            datetime
            .fromisoformat(request.POST['date_to'])
            .replace(hour=0, minute=0, second=0)
        )

        timestamp_from = dt_from.timestamp()
        timestamp_to = dt_to.timestamp()

        onpbx_client = OnpbxClient(employee.onpbx_account.subdomain, employee.onpbx_account.api_key)

        sipuni_account = employee.sipuni_account
        sipuni_client = None
        if sipuni_account:
            sipuni_client = sipuni_account.client

        calculator = SalaryCounter(employee, onpbx_client, sipuni_client)
        report = asyncio.run(calculator.get_detailed_report(timestamp_from, timestamp_to))
        report.employee = employee
        report.date_from = dt_from
        report.date_to = dt_to

        return render(request, "salaries/salary_result.html", {
            "report": report,
            'save_form': SalaryReportForm(instance=report)
        })


class SalesPlanView(View):

    @xframe_options_exempt
    def get(self, request, *args, **kwargs):

        auth_key = request.GET.get('auth_key')
        if auth_key != 'eo485yngw8oer9jvwiertu6bei7ty':
            return HttpResponse("Access denied!")

        get_params = request.GET.dict()

        interval = create_interval(**get_params)

        f = ApiIterator(
            url=SalaryCounter.LEADS_FETCH_URL,
            params={
                'auth_key': SalaryCounter.AUTH_KEY,
                "filter": json.dumps({
                    'closed_at': {
                        "from": interval.get_timestamp_from(),
                        "to": interval.get_timestamp_to()
                    },
                    "statuses": [
                        {"status_id": 142, "pipeline_id": 1212574},
                        {"status_id": 142, "pipeline_id": 1693621},
                        {"status_id": 142, "pipeline_id": 1693720},
                        {"status_id": 142, "pipeline_id": 3941655},
                        {"status_id": 142, "pipeline_id": 3346951},
                        {"status_id": 142, "pipeline_id": 3964107},
                        {"status_id": 142, "pipeline_id": 3678177},
                        {"status_id": 142, "pipeline_id": 4669350}
                    ]
                })
            },
            entity_type='leads',
            fetch_limit=50
        )

        leads_total_sales = {}
        employees = get_all_active_employees().filter(show_in_sales_plan=True).all()

        for lead in f.get_next():
            employee_id = lead['responsible_user_id']
            if not leads_total_sales.get(employee_id):
                leads_total_sales[employee_id] = 0
            leads_total_sales[employee_id] += lead['price']

        stats = []

        display_mods = {
            'percent': lambda actual, plan, percent: {
                'label': f"{percent}%",
                'bar_width': math.ceil(percent)
            },

            'money': lambda actual, plan, percent: {
                'label': f"{actual:,} руб.",
                'bar_width': 100
            },

            'all': lambda actual, plan, percent: {
                "label": f"{actual:,} руб. / {plan:,} руб. ({percent}%)",
                'bar_width': math.ceil(percent)
            }
        }

        for employee in employees:
            plan = employee.sales_plan if employee.sales_plan is not None else 0
            percent = 0 if plan == 0 else round(
                (leads_total_sales.get(employee.amocrm_id, 0) / plan) * 100, 2)
            actual = leads_total_sales.get(employee.amocrm_id, 0)
            stat = {
                'employee': employee,
                'actual': actual,
                'plan': plan,
                'percent': percent,
            }

            display_stat_options = display_mods[request.GET.get(
                'display_mode', 'all')](actual, plan, percent)
            if display_stat_options['bar_width'] < 20:
                display_stat_options['bar_width'] = 20

            stat.update(display_stat_options)
            stats.append(stat)

        return render(request, "amo_dashboards/sales_plan_progress.html", {
            'stats': stats
        })
