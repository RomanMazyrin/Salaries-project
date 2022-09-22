from django.urls import path
from . import views

app_name = "salaries"

urlpatterns = [
    path("", views.IndexView.as_view(template_name="salaries/main.html"), name="index"),
    path("my-reports-list", views.MyReportsListView.as_view(), name="my_reports_list"),
    path("salary-result", views.SalaryResultView.as_view(), name="salary_result"),
    path("sales-plan-progress", views.SalesPlanView.as_view(), name="sales_plan_progress"),
    path(
        "salary-report/create",
        views.SalaryReportCreateView.as_view(),
        name="salary_report_create",
    ),
    path(
        "salary-report/view/<slug:report_slug>",
        views.SalaryReportView.as_view(),
        name="salary_report_view",
    ),
    path("api/salary-report/<slug_id>", views.SalaryReportApiView.as_view()),
]
