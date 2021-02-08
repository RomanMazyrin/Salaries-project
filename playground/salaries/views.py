from django.http import HttpResponse
from django.views import generic, View
from django.shortcuts import render, get_object_or_404
from .models import Employee
from datetime import datetime
from packages.Onlinepbx.Client import Client
from .services.SalaryCounter.SalaryCounter import SalaryCounter


class IndexView(generic.ListView):

    def get_queryset(self):
        return Employee.objects.all()


class SalaryResultView(View):

    def post(self, request, *args, **kwargs):
        employee = get_object_or_404(Employee, pk=kwargs['employee_id'])
        timestamp_from = datetime.fromisoformat(request.POST['date_from']).timestamp()
        timestamp_to = datetime\
            .fromisoformat(request.POST['date_to'])\
            .replace(hour=23, minute=59, second=59)\
            .timestamp()

        client = Client(employee.onpbx_account.subdomain, employee.onpbx_account.api_key)
        calculator = SalaryCounter(client)
        report = calculator.get_detailed_report(employee, timestamp_from, timestamp_to)

        report.update({
            'employee': employee,
            'from': request.POST['date_from'],
            'to': request.POST['date_to'],
        })

        return render(request, "salaries/salary_result.html", report)
