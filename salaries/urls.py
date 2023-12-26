from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

app_name = "salaries"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/login/", auth_views.LoginView.as_view(redirect_authenticated_user=True)),
    path("auth/", include("django.contrib.auth.urls")),
    path("", include("django_prometheus.urls")),
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
