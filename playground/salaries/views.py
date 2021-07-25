from django.views import generic, View
from django.shortcuts import render, get_object_or_404
from .models import Employee
from datetime import datetime
from packages.Onlinepbx.Client import Client
from .services.SalaryCounter.SalaryCounter import SalaryCounter
from .services.SalaryCounter.Report import Report
import pytz
from django.contrib.auth.mixins import LoginRequiredMixin


class IndexView(LoginRequiredMixin, generic.ListView):

    def get_queryset(self):
        return Employee.objects.order_by("pk").all()


class SalaryResultView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):

        employee = get_object_or_404(Employee, pk=kwargs['employee_id'])

        timezone = pytz.timezone("Europe/Moscow")

        timestamp_from = timezone.localize(datetime\
            .fromisoformat(request.POST['date_from'])\
            .replace(hour=0, minute=0, second=0)\
        ).timestamp()

        timestamp_to = timezone.localize(datetime\
            .fromisoformat(request.POST['date_to'])\
            .replace(hour=23, minute=59, second=59)\
        ).timestamp()

        client = Client(employee.onpbx_account.subdomain, employee.onpbx_account.api_key)
        calculator = SalaryCounter(employee, client, Report())
        report = calculator.get_detailed_report(timestamp_from, timestamp_to)

        return render(request, "salaries/salary_result.html", {
            "report": report,
            'employee': employee,
            'from': request.POST['date_from'],
            'to': request.POST['date_to']
        })
