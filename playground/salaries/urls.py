from django.urls import path

from . import views

app_name = "salaries"

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('salary-result/<int:employee_id>', views.SalaryResultView.as_view(), name='salary_result')
]
