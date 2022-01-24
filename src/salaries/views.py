from django.http.response import HttpResponse
from django.views import generic, View
from django.shortcuts import render, get_object_or_404

from amocrm_components.ApiIterator import ApiIterator
from .models import Employee
from datetime import datetime
from packages.Onlinepbx.Client import Client
from .services.SalaryCounter.SalaryCounter import SalaryCounter
import pytz
from django.contrib.auth.mixins import LoginRequiredMixin
import json
import math
from .services.DateIntervals.DashboardDateInterval import create_interval
from django.views.decorators.clickjacking import xframe_options_exempt


class IndexView(LoginRequiredMixin, generic.ListView):

    def get_queryset(self):
        return Employee.objects.order_by("pk").all()


class SalaryResultView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):

        employee = get_object_or_404(Employee, pk=kwargs['employee_id'])

        timezone = pytz.timezone("Europe/Moscow")

        timestamp_from = timezone.localize(datetime
                                           .fromisoformat(request.POST['date_from'])
                                           .replace(hour=0, minute=0, second=0)
                                           ).timestamp()

        timestamp_to = timezone.localize(datetime
                                         .fromisoformat(request.POST['date_to'])
                                         .replace(hour=23, minute=59, second=59)
                                         ).timestamp()

        client = Client(employee.onpbx_account.subdomain, employee.onpbx_account.api_key)
        calculator = SalaryCounter(employee, client)
        report = calculator.get_detailed_report(timestamp_from, timestamp_to)

        return render(request, "salaries/salary_result.html", {
            "report": report,
            'employee': employee,
            'from': request.POST['date_from'],
            'to': request.POST['date_to']
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
        employees = Employee.objects.order_by("pk").all()

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